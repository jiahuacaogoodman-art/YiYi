import { Button, Card, Col, Form, Input, InputNumber, Modal, Progress, Row, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ChevronLeft, ChevronRight, Layers3, RotateCcw } from "lucide-react";
import { practiceApi, questionApi, taxonomyApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import type { Chapter, KnowledgePoint, PracticeAnswerResult, Question, Subject } from "../../types/domain";

const modes = [
  { label: "顺序刷题", value: "sequential" },
  { label: "随机刷题", value: "random" },
  { label: "错题重刷", value: "wrong" },
  { label: "收藏练习", value: "favorites" },
  { label: "未做题", value: "unanswered" },
  { label: "高频错题", value: "high_wrong" },
];

export function PracticePage() {
  const [params] = useSearchParams();
  const [form] = Form.useForm();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [points, setPoints] = useState<KnowledgePoint[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [results, setResults] = useState<Record<number, PracticeAnswerResult>>({});
  const [loading, setLoading] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

  const current = questions[index];
  const progress = questions.length ? Math.round(((index + 1) / questions.length) * 100) : 0;

  useEffect(() => {
    taxonomyApi.subjects({ enabled: true, page_size: 100 }).then((data) => setSubjects(data.items));
  }, []);

  useEffect(() => {
    const subjectId = params.get("subject_id");
    const chapterId = params.get("chapter_id");
    const knowledgePointId = params.get("knowledge_point_id");
    form.setFieldsValue({
      mode: params.get("mode") || "sequential",
      subject_id: subjectId ? Number(subjectId) : undefined,
      chapter_id: chapterId ? Number(chapterId) : undefined,
      knowledge_point_id: knowledgePointId ? Number(knowledgePointId) : undefined,
      question_count: 20,
    });
    if (subjectId) loadChapters(Number(subjectId));
    if (chapterId) loadPoints(Number(chapterId));
  }, [form, params]);

  const loadChapters = async (subjectId?: number) => {
    setChapters([]);
    setPoints([]);
    if (!subjectId) return;
    const data = await taxonomyApi.chapters({ subject_id: subjectId, enabled: true, page_size: 200 });
    setChapters(data.items);
  };

  const loadPoints = async (chapterId?: number) => {
    setPoints([]);
    if (!chapterId) return;
    const data = await taxonomyApi.knowledgePoints({ chapter_id: chapterId, enabled: true, page_size: 200 });
    setPoints(data.items);
  };

  const start = async () => {
    const values = form.getFieldsValue();
    setLoading(true);
    try {
      const data = await practiceApi.start(values);
      setQuestions(data.questions);
      setIndex(0);
      setAnswers({});
      setResults({});
      if (!data.questions.length) message.info("当前条件下暂无可练习题目");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!current) return;
    const result = await practiceApi.answer({
      question_id: current.id,
      answer: answers[current.id],
      mode: form.getFieldValue("mode"),
    });
    setResults((currentResults) => ({ ...currentResults, [current.id]: result }));
  };

  const toggleFavorite = async () => {
    if (!current) return;
    if (current.is_favorited) {
      await questionApi.unfavorite(current.id);
      message.success("已取消收藏");
    } else {
      await questionApi.favorite(current.id);
      message.success("已收藏");
    }
    setQuestions((items) => items.map((item) => (item.id === current.id ? { ...item, is_favorited: !item.is_favorited } : item)));
  };

  const sendFeedback = async () => {
    if (!current || !feedbackText.trim()) return;
    await questionApi.feedback(current.id, { feedback_type: "content_error", content: feedbackText.trim() });
    message.success("反馈已提交");
    setFeedbackText("");
    setFeedbackOpen(false);
  };

  const result = current ? results[current.id] : undefined;

  const answerSheet = useMemo(
    () =>
      questions.map((item, itemIndex) => (
        <Button
          key={item.id}
          type={itemIndex === index ? "primary" : results[item.id] ? results[item.id].is_correct ? "default" : "dashed" : "default"}
          danger={Boolean(results[item.id] && !results[item.id].is_correct)}
          onClick={() => setIndex(itemIndex)}
        >
          {itemIndex + 1}
        </Button>
      )),
    [index, questions, results],
  );

  return (
    <div className="page">
      <section className="practice-hero">
        <div>
          <span>训练中心</span>
          <Typography.Title level={1}>把每一道题都变成复盘资产</Typography.Title>
          <Typography.Text>顺序、随机、章节、错题、收藏和高频错题练习都在这里开始。</Typography.Text>
        </div>
        <div className="practice-hero__status">
          <strong>{questions.length ? `${index + 1}/${questions.length}` : "待开始"}</strong>
          <span>{questions.length ? "当前进度" : "选择条件后开练"}</span>
        </div>
      </section>
      <div className="panel practice-filter-panel">
        <Form form={form} layout="inline" className="filter-form">
          <Form.Item name="mode" label="模式">
            <Select options={modes} style={{ width: 140 }} />
          </Form.Item>
          <Form.Item name="subject_id" label="科目">
            <Select
              allowClear
              style={{ width: 180 }}
              options={subjects.map((item) => ({ label: item.name, value: item.id }))}
              onChange={(value) => {
                form.setFieldsValue({ chapter_id: undefined, knowledge_point_id: undefined });
                loadChapters(value);
              }}
            />
          </Form.Item>
          <Form.Item name="chapter_id" label="章节">
            <Select
              allowClear
              style={{ width: 180 }}
              options={chapters.map((item) => ({ label: item.name, value: item.id }))}
              onChange={(value) => {
                form.setFieldsValue({ knowledge_point_id: undefined });
                loadPoints(value);
              }}
            />
          </Form.Item>
          <Form.Item name="knowledge_point_id" label="知识点">
            <Select allowClear style={{ width: 180 }} options={points.map((item) => ({ label: item.name, value: item.id }))} />
          </Form.Item>
          <Form.Item name="question_count" label="题量">
            <InputNumber min={1} max={200} />
          </Form.Item>
          <Button type="primary" icon={<RotateCcw size={16} />} onClick={start} loading={loading}>生成训练</Button>
        </Form>
      </div>

      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={17}>
          <Card variant="borderless" className="question-card">
            {current ? (
              <>
                <div className="practice-head">
                  <Space>
                    <Tag color="blue">第 {index + 1} / {questions.length} 题</Tag>
                    {result ? <Tag color={result.is_correct ? "green" : "red"}>{result.is_correct ? "回答正确" : "回答错误"}</Tag> : null}
                  </Space>
                  <Progress percent={progress} size="small" />
                </div>
                <QuestionViewer
                  question={current}
                  value={answers[current.id]}
                  submitted={Boolean(result)}
                  correctAnswer={result?.correct_answer}
                  analysis={result?.analysis}
                  onChange={(answer) => setAnswers((currentAnswers) => ({ ...currentAnswers, [current.id]: answer }))}
                  onSubmit={submit}
                  onFavorite={toggleFavorite}
                  onFeedback={() => setFeedbackOpen(true)}
                />
                <div className="question-nav">
                  <Button icon={<ChevronLeft size={16} />} disabled={index === 0} onClick={() => setIndex(index - 1)}>
                    上一题
                  </Button>
                  <Button icon={<ChevronRight size={16} />} disabled={index >= questions.length - 1} onClick={() => setIndex(index + 1)}>
                    下一题
                  </Button>
                </div>
              </>
            ) : (
              <div className="empty-workspace">
                <span className="empty-workspace__icon"><Layers3 size={30} /></span>
                <Typography.Title level={4}>选择条件后开始练习</Typography.Title>
                <Typography.Text type="secondary">系统会从已发布题库中抽取题目，生成一组适合当前目标的训练。</Typography.Text>
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} xl={7}>
          <div className="panel sticky-panel">
            <div className="panel-title">题号导航</div>
            <div className="answer-sheet">{answerSheet}</div>
          </div>
        </Col>
      </Row>

      <Modal title="这题有问题" open={feedbackOpen} onOk={sendFeedback} onCancel={() => setFeedbackOpen(false)} okText="提交反馈">
        <Input.TextArea rows={5} value={feedbackText} onChange={(event) => setFeedbackText(event.target.value)} placeholder="请描述题干、答案、解析或分类的问题" />
      </Modal>
    </div>
  );
}