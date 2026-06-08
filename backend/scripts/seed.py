from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.settings import SystemSetting
from app.models.taxonomy import Chapter, KnowledgePoint, Subject
from app.models.user import Role, User
from app.schemas.question import QuestionCreate, QuestionOptionIn
from app.services.import_service import generate_template
from app.services.question_service import create_question


SUBJECTS = [
    ("医学免疫学", "immunology", "shield-plus"),
    ("病原生物学", "pathogen-biology", "bug"),
    ("生理学", "physiology", "activity"),
    ("病理学", "pathology", "microscope"),
    ("药理学", "pharmacology", "pill"),
]

IMMUNOLOGY_CHAPTERS = [
    "抗原",
    "免疫球蛋白",
    "补体系统",
    "T 细胞免疫",
    "B 细胞免疫",
    "超敏反应",
    "免疫缺陷病",
]

QUESTIONS = [
    {
        "chapter": "抗原",
        "kp": "抗原决定簇",
        "type": "single_choice",
        "stem": "决定抗原特异性的基本结构是？",
        "options": ["抗原决定簇", "载体蛋白", "佐剂", "补体片段"],
        "answer": "A",
        "analysis": "抗原决定簇又称表位，是被抗体或 TCR 特异性识别的结构基础。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "抗原",
        "kp": "半抗原",
        "type": "single_choice",
        "stem": "半抗原本身通常具备哪种特性？",
        "options": ["只有免疫反应性，无免疫原性", "既无免疫反应性也无免疫原性", "只有免疫原性", "可直接诱导强免疫应答"],
        "answer": "A",
        "analysis": "半抗原能与抗体结合，但单独不能诱导免疫应答，需要与载体结合后才具备免疫原性。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "抗原",
        "kp": "TD抗原",
        "type": "true_false",
        "stem": "TD 抗原诱导 B 细胞产生抗体通常需要 T 细胞辅助。",
        "options": ["正确", "错误"],
        "answer": "A",
        "analysis": "TD 抗原即胸腺依赖性抗原，需要 CD4+ T 细胞辅助 B 细胞活化、类别转换和亲和力成熟。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "免疫球蛋白",
        "kp": "抗体结构",
        "type": "single_choice",
        "stem": "免疫球蛋白分子中主要负责结合抗原的区域是？",
        "options": ["可变区", "恒定区", "铰链区", "Fc 段"],
        "answer": "A",
        "analysis": "抗体重链和轻链的可变区共同形成抗原结合部位，决定抗原特异性。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "免疫球蛋白",
        "kp": "抗体功能",
        "type": "multiple_choice",
        "stem": "下列属于抗体主要生物学功能的是？",
        "options": ["中和毒素", "调理吞噬", "激活补体", "直接复制遗传物质"],
        "answer": "ABC",
        "analysis": "抗体可中和病原体或毒素、通过 Fc 段介导调理吞噬，并可经典途径激活补体。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "免疫球蛋白",
        "kp": "IgG",
        "type": "single_choice",
        "stem": "唯一能通过胎盘的免疫球蛋白类别是？",
        "options": ["IgA", "IgD", "IgG", "IgM"],
        "answer": "C",
        "analysis": "IgG 可经 FcRn 介导通过胎盘，为新生儿提供被动免疫保护。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "补体系统",
        "kp": "经典途径",
        "type": "single_choice",
        "stem": "补体经典途径的启动通常依赖于？",
        "options": ["抗原抗体复合物", "病原体甘露糖", "C3 自发水解", "IL-2 分泌"],
        "answer": "A",
        "analysis": "经典途径由 C1q 识别结合抗原抗体复合物中的 Fc 段后启动。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "补体系统",
        "kp": "膜攻击复合物",
        "type": "single_choice",
        "stem": "形成膜攻击复合物的补体终末成分主要是？",
        "options": ["C1-C3", "C3a-C5a", "C5b-C9", "B因子-D因子"],
        "answer": "C",
        "analysis": "C5b 与 C6、C7、C8、C9 组装形成膜攻击复合物，导致靶细胞裂解。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "补体系统",
        "kp": "过敏毒素",
        "type": "multiple_choice",
        "stem": "具有过敏毒素作用的补体片段包括？",
        "options": ["C3a", "C4a", "C5a", "C9"],
        "answer": "ABC",
        "analysis": "C3a、C4a、C5a 可促进肥大细胞脱颗粒和炎症反应，其中 C5a 活性最强。",
        "difficulty": "hard",
        "importance": "key",
    },
    {
        "chapter": "T 细胞免疫",
        "kp": "TCR识别",
        "type": "single_choice",
        "stem": "能特异性识别抗原肽-MHC 复合物的细胞是？",
        "options": ["B细胞", "T细胞", "红细胞", "血小板"],
        "answer": "B",
        "analysis": "T 细胞通过 TCR 识别抗原呈递细胞表面的抗原肽-MHC 复合物。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "T 细胞免疫",
        "kp": "CD4 T细胞",
        "type": "single_choice",
        "stem": "CD4+ T 细胞主要识别由哪类 MHC 分子呈递的抗原？",
        "options": ["MHC I 类", "MHC II 类", "CD1 分子", "补体受体"],
        "answer": "B",
        "analysis": "CD4+ T 细胞识别 MHC II 类分子呈递的外源性抗原肽。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "T 细胞免疫",
        "kp": "CTL",
        "type": "true_false",
        "stem": "CTL 主要通过释放穿孔素和颗粒酶杀伤靶细胞。",
        "options": ["正确", "错误"],
        "answer": "A",
        "analysis": "细胞毒性 T 细胞可通过穿孔素/颗粒酶途径或 Fas/FasL 途径诱导靶细胞死亡。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "B 细胞免疫",
        "kp": "BCR",
        "type": "single_choice",
        "stem": "成熟 B 细胞表面识别抗原的主要受体是？",
        "options": ["BCR", "TCR", "CD3", "MHC I"],
        "answer": "A",
        "analysis": "BCR 是膜型免疫球蛋白与信号转导分子组成的复合体，可直接识别天然抗原。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "B 细胞免疫",
        "kp": "浆细胞",
        "type": "single_choice",
        "stem": "B 细胞分化后主要分泌抗体的终末效应细胞是？",
        "options": ["浆细胞", "NK细胞", "树突状细胞", "中性粒细胞"],
        "answer": "A",
        "analysis": "活化 B 细胞可分化为浆细胞，浆细胞是大量分泌抗体的主要细胞。",
        "difficulty": "easy",
        "importance": "key",
    },
    {
        "chapter": "B 细胞免疫",
        "kp": "免疫记忆",
        "type": "multiple_choice",
        "stem": "再次免疫应答的特点包括？",
        "options": ["潜伏期短", "抗体效价高", "亲和力更高", "完全不需要抗原刺激"],
        "answer": "ABC",
        "analysis": "再次应答因记忆细胞存在而更快、更强，抗体亲和力更高，但仍需抗原刺激。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "超敏反应",
        "kp": "I型超敏反应",
        "type": "single_choice",
        "stem": "I 型超敏反应主要由哪类抗体介导？",
        "options": ["IgE", "IgG", "IgM", "IgA"],
        "answer": "A",
        "analysis": "I 型超敏反应由 IgE 介导，肥大细胞和嗜碱性粒细胞脱颗粒参与反应。",
        "difficulty": "easy",
        "importance": "frequent",
    },
    {
        "chapter": "超敏反应",
        "kp": "II型超敏反应",
        "type": "true_false",
        "stem": "II 型超敏反应又称细胞毒型超敏反应。",
        "options": ["正确", "错误"],
        "answer": "A",
        "analysis": "II 型超敏反应由 IgG 或 IgM 结合细胞表面抗原后引起补体或效应细胞介导的损伤。",
        "difficulty": "medium",
        "importance": "key",
    },
    {
        "chapter": "超敏反应",
        "kp": "IV型超敏反应",
        "type": "single_choice",
        "stem": "结核菌素试验阳性主要体现哪型超敏反应？",
        "options": ["I型", "II型", "III型", "IV型"],
        "answer": "D",
        "analysis": "结核菌素试验是由 T 细胞介导的迟发型超敏反应，属于 IV 型超敏反应。",
        "difficulty": "medium",
        "importance": "frequent",
    },
    {
        "chapter": "免疫缺陷病",
        "kp": "原发性免疫缺陷",
        "type": "single_choice",
        "stem": "X 连锁无丙种球蛋白血症主要缺陷发生在？",
        "options": ["B 细胞发育", "T 细胞阳性选择", "补体 C9 合成", "中性粒细胞趋化"],
        "answer": "A",
        "analysis": "该病由 BTK 基因缺陷导致 B 细胞发育阻滞，外周成熟 B 细胞和免疫球蛋白显著减少。",
        "difficulty": "hard",
        "importance": "key",
    },
    {
        "chapter": "免疫缺陷病",
        "kp": "获得性免疫缺陷",
        "type": "single_choice",
        "stem": "HIV 主要感染并破坏的免疫细胞是？",
        "options": ["CD4+ T 细胞", "红细胞", "血小板", "嗜酸性粒细胞"],
        "answer": "A",
        "analysis": "HIV 通过 CD4 分子及辅助受体进入细胞，主要破坏 CD4+ T 细胞，导致细胞免疫功能下降。",
        "difficulty": "easy",
        "importance": "frequent",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        admin = seed_admin(db)
        seed_taxonomy(db)
        seed_questions(db, admin)
        seed_exam(db, admin)
        seed_settings(db)
        db.commit()
        generate_template()
        print("Seed 数据已完成")
    finally:
        db.close()


def seed_roles(db):
    roles = [
        ("student", "普通用户", "学生端刷题用户"),
        ("admin", "管理员", "题库和运营后台管理员"),
        ("super_admin", "超级管理员", "拥有所有权限"),
    ]
    for name, label, description in roles:
        if not db.scalar(select(Role).where(Role.name == name)):
            db.add(Role(name=name, label=label, description=description))
    db.flush()


def seed_admin(db) -> User:
    role = db.scalar(select(Role).where(Role.name == "super_admin"))
    admin = db.scalar(select(User).where(User.username == settings.default_admin_username))
    if admin:
        return admin
    admin = User(
        username=settings.default_admin_username,
        nickname="默认管理员",
        hashed_password=get_password_hash(settings.default_admin_password),
        role_id=role.id,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    return admin


def seed_taxonomy(db):
    subjects = {}
    for index, (name, code, icon) in enumerate(SUBJECTS, start=1):
        subject = db.scalar(select(Subject).where(Subject.name == name))
        if not subject:
            subject = Subject(name=name, code=code, icon=icon, sort_order=index, is_enabled=True)
            db.add(subject)
            db.flush()
        subjects[name] = subject
    immunology = subjects["医学免疫学"]
    for index, chapter_name in enumerate(IMMUNOLOGY_CHAPTERS, start=1):
        chapter = db.scalar(
            select(Chapter).where(Chapter.subject_id == immunology.id, Chapter.name == chapter_name)
        )
        if not chapter:
            chapter = Chapter(
                subject_id=immunology.id,
                name=chapter_name,
                code=f"immunology-{index}",
                sort_order=index,
                is_enabled=True,
            )
            db.add(chapter)
            db.flush()
    for item in QUESTIONS:
        chapter = db.scalar(select(Chapter).where(Chapter.subject_id == immunology.id, Chapter.name == item["chapter"]))
        kp = db.scalar(
            select(KnowledgePoint).where(KnowledgePoint.chapter_id == chapter.id, KnowledgePoint.name == item["kp"])
        )
        if not kp:
            db.add(
                KnowledgePoint(
                    subject_id=immunology.id,
                    chapter_id=chapter.id,
                    name=item["kp"],
                    label=item["kp"],
                    importance_level="high" if item["importance"] == "frequent" else "medium",
                    sort_order=1,
                    is_enabled=True,
                )
            )
            db.flush()


def seed_questions(db, admin: User):
    immunology = db.scalar(select(Subject).where(Subject.name == "医学免疫学"))
    for item in QUESTIONS:
        exists = db.scalar(select(Question).where(Question.stem == item["stem"]))
        if exists:
            continue
        chapter = db.scalar(select(Chapter).where(Chapter.subject_id == immunology.id, Chapter.name == item["chapter"]))
        kp = db.scalar(select(KnowledgePoint).where(KnowledgePoint.chapter_id == chapter.id, KnowledgePoint.name == item["kp"]))
        options = [
            QuestionOptionIn(option_key=chr(65 + index), content=content, sort_order=index + 1)
            for index, content in enumerate(item["options"])
        ]
        payload = QuestionCreate(
            stem=item["stem"],
            question_type=item["type"],
            options=options,
            correct_answer=item["answer"],
            analysis=item["analysis"],
            subject_id=immunology.id,
            chapter_id=chapter.id,
            knowledge_point_id=kp.id,
            difficulty=item["difficulty"],
            importance=item["importance"],
            source="self_built",
            year=2026,
            tags=[item["chapter"], item["kp"]],
            status="published",
        )
        create_question(db, payload, admin)
    db.flush()


def seed_exam(db, admin: User):
    if db.scalar(select(Exam).where(Exam.name == "医学免疫学基础模拟考试")):
        return
    immunology = db.scalar(select(Subject).where(Subject.name == "医学免疫学"))
    questions = db.scalars(
        select(Question).where(Question.subject_id == immunology.id, Question.status == "published").order_by(Question.id).limit(10)
    ).all()
    exam = Exam(
        name="医学免疫学基础模拟考试",
        exam_type="mock",
        subject_id=immunology.id,
        total_score=100,
        pass_score=60,
        duration_minutes=30,
        is_public=True,
        status="published",
        created_by_id=admin.id,
        description="覆盖抗原、抗体、补体、T/B 细胞免疫等基础内容。",
    )
    db.add(exam)
    db.flush()
    for index, question in enumerate(questions, start=1):
        db.add(ExamQuestion(exam_id=exam.id, question_id=question.id, score=10, sort_order=index))


def seed_settings(db):
    defaults = [
        ("site_name", "医学刷题平台", "站点名称", True),
        ("ai_question_generation_enabled", "false", "预留 AI 出题开关", False),
        ("ai_explanation_enabled", "false", "预留 AI 解析开关", False),
        ("knowledge_graph_enabled", "false", "预留知识图谱开关", False),
    ]
    for key, value, description, is_public in defaults:
        if not db.scalar(select(SystemSetting).where(SystemSetting.key == key)):
            db.add(SystemSetting(key=key, value=value, description=description, is_public=is_public))


if __name__ == "__main__":
    main()
