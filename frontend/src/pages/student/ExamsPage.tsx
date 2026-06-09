import { Button, Card, Col, Empty, Modal, Progress, Row, Space, Tag, Typography, message } from "antd";
import { useEffect, useMemo, useState } from "react";
import { Clock, FileCheck2 } from "lucide-react";
import { Link } from "react-router-dom";
import { examApi, taxonomyApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import type { Exam, ExamRecord, ExamStart, Subject } from "../../types/domain";

export function ExamsPage() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [active, setActive] = useState<ExamStart | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [record, setRecord] = useState<ExamRecord | null>(null);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    Promise.all([examApi.publicList({ page_size: 100 }), taxonomyApi.subjects({ page_size: 100 })]).then(([examData, subjectData]) => {
      setExams(examData.items);
      setSubjects(subjectData.items);
    });
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const start = async (exam: Exam) => {
    const data = await examApi.start(exam.id);
    setActive(data);
    setAnswers({});
    setRecord(null);
  };

  const submit = async () => {
    if (!active) return;
    const data = await examApi.submit(active.exam.id, {
      record_id: active.record_id,
      answers: Object.entries(answers).map(([question_id, answer]) => ({ question_id: Number(question_id), answer })),
    });
    setRecord(data);
    message.success("试卷已提交");
  };

  const remaining = useMemo(() => {
    if (!active) return 0;
    return Math.max(0, new Date(active.deadline_at).getTime() - now);
  }, [active, now]);

  const minutes = Math.floor(remaining / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  const activeQuestions = active?.exam.questions || [];
  const answeredCount = Object.values(answers).filter(Boolean).length;
  const recordAnswerMap = useMemo(() => {
    const map = new Map<number, { is_correct?: boolean; answer?: string }>();
    (record?.answers || []).forEach((item) => {
      map.set(Number(item.question_id), {
        is_correct: Boolean(item.is_correct),
        answer: String(item.answer || ""),
      });
    });
    return map;
  }, [record]);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>模拟考试</Typography.Title>
          <Typography.Text type="secondary">选择管理员发布的试卷，限时作答并查看成绩解析。</Typography.Text>
        </div>
      </div>
      <Row gutter={[16, 16]}>
        {exams.length ? (
          exams.map((exam) => (
            <Col xs={24} md={12} xl={8} key={exam.id}>
              <Card variant="borderless" className="exam-card">
                <Typography.Title level={4}>{exam.name}</Typography.Title>
                <Typography.Paragraph type="secondary">{exam.description || "标准模拟考试"}</Typography.Paragraph>
                <Space wrap>
                  <Tag>{subjects.find((item) => item.id === exam.subject_id)?.name || exam.subject_name || "综合"}</Tag>
                  <Tag>{exam.question_count} 题</Tag>
                  <Tag>{exam.duration_minutes} 分钟</Tag>
                  <Tag color="blue">{exam.total_score} 分</Tag>
                </Space>
                <Button type="primary" icon={<FileCheck2 size={16} />} onClick={() => start(exam)}>
                  开始考试
                </Button>
              </Card>
            </Col>
          ))
        ) : (
          <Col span={24}>
            <div className="panel">
              <Empty description="暂无已发布试卷" />
            </div>
          </Col>
        )}
      </Row>

      <Modal
        title={active?.exam.name || "模拟考试"}
        open={Boolean(active)}
        width={1120}
        onCancel={() => setActive(null)}
        footer={null}
        className="exam-modal"
      >
        {active ? (
          <>
            <div className="exam-toolbar">
              <Space wrap>
                <Tag icon={<Clock size={14} />} color={remaining < 5 * 60 * 1000 ? "red" : "blue"}>
                  剩余 {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
                </Tag>
                <Tag>{answeredCount} / {activeQuestions.length} 已答</Tag>
              </Space>
              <Button type="primary" danger onClick={submit} disabled={Boolean(record)}>
                交卷
              </Button>
            </div>
            <Progress percent={activeQuestions.length ? Math.round((answeredCount / activeQuestions.length) * 100) : 0} />
            {record ? (
              <div className="exam-result">
                <Typography.Title level={3}>得分 {record.score ?? 0}</Typography.Title>
                <Typography.Text>
                  正确 {record.correct_count} 题，错误 {record.wrong_count} 题
                </Typography.Text>
                <Typography.Paragraph type="secondary">
                  正确率 {activeQuestions.length ? Math.round((record.correct_count / activeQuestions.length) * 100) : 0}%
                </Typography.Paragraph>
                <div className="section-actions">
                  <Link to="/practice?mode=wrong">
                    <Button type="primary">重新练习错题</Button>
                  </Link>
                </div>
              </div>
            ) : null}
            <div className="exam-answer-card">
              <div className="panel-title">答题卡</div>
              <div className="answer-sheet">
                {activeQuestions.map((question, questionIndex) => {
                  const answer = recordAnswerMap.get(question.id);
                  return (
                    <Button
                      key={question.id}
                      danger={answer ? answer.is_correct === false : false}
                      type={answers[question.id] || answer ? "primary" : "default"}
                    >
                      {questionIndex + 1}
                    </Button>
                  );
                })}
              </div>
            </div>
            <Space direction="vertical" size={18} className="full-width">
              {activeQuestions.map((question, questionIndex) => (
                <Card key={question.id} variant="borderless">
                  <Space wrap>
                    <Tag color="blue">第 {questionIndex + 1} 题</Tag>
                    {recordAnswerMap.has(question.id) ? (
                      <Tag color={recordAnswerMap.get(question.id)?.is_correct ? "green" : "red"}>
                        {recordAnswerMap.get(question.id)?.is_correct ? "正确" : "错误"}
                      </Tag>
                    ) : null}
                  </Space>
                  <QuestionViewer
                    question={question}
                    value={answers[question.id]}
                    submitted={Boolean(record)}
                    onChange={(answer) => setAnswers((current) => ({ ...current, [question.id]: answer }))}
                  />
                </Card>
              ))}
            </Space>
          </>
        ) : null}
      </Modal>
    </div>
  );
}