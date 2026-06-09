import { Button, Checkbox, Form, Image, Input, Radio, Space, Tag, Typography } from "antd";
import { Flag, Heart, MessageSquareWarning } from "lucide-react";
import type { Question } from "../types/domain";
import { difficultyLabel, questionTypeLabel } from "../utils/format";

interface QuestionViewerProps {
  question: Question;
  value?: string;
  submitted?: boolean;
  correctAnswer?: string;
  analysis?: string;
  onChange?: (answer: string) => void;
  onSubmit?: () => void;
  onFavorite?: () => void;
  onFeedback?: () => void;
}

export function QuestionViewer({
  question,
  value,
  submitted,
  correctAnswer,
  analysis,
  onChange,
  onSubmit,
  onFavorite,
  onFeedback,
}: QuestionViewerProps) {
  const type = question.question_type;
  const selected = value || "";
  const correct = correctAnswer || question.correct_answer;

  const renderInput = () => {
    if (type === "single_choice" || type === "true_false") {
      return (
        <Radio.Group className="answer-options" value={selected} onChange={(event) => onChange?.(event.target.value)}>
          <Space direction="vertical" size={10}>
            {(question.options || []).map((option) => (
              <Radio key={option.option_key} value={option.option_key} className="answer-option">
                <strong>{option.option_key}.</strong> {option.content}
                {option.image_url ? <Image src={option.image_url} width={120} /> : null}
              </Radio>
            ))}
          </Space>
        </Radio.Group>
      );
    }
    if (type === "multiple_choice") {
      const values = selected ? selected.split(",").filter(Boolean) : [];
      return (
        <Checkbox.Group
          className="answer-options"
          value={values}
          onChange={(items) => onChange?.(items.map(String).sort().join(","))}
        >
          <Space direction="vertical" size={10}>
            {(question.options || []).map((option) => (
              <Checkbox key={option.option_key} value={option.option_key} className="answer-option">
                <strong>{option.option_key}.</strong> {option.content}
                {option.image_url ? <Image src={option.image_url} width={120} /> : null}
              </Checkbox>
            ))}
          </Space>
        </Checkbox.Group>
      );
    }
    if (type === "short_answer") {
      return <Input.TextArea rows={5} value={selected} onChange={(event) => onChange?.(event.target.value)} placeholder="请输入你的作答" />;
    }
    return <Input value={selected} onChange={(event) => onChange?.(event.target.value)} placeholder="请输入答案" />;
  };

  return (
    <div className="question-viewer">
      <div className="question-viewer__meta">
        <Tag color="blue">{questionTypeLabel[type] || type}</Tag>
        <Tag color={question.difficulty === "hard" ? "red" : question.difficulty === "easy" ? "green" : "gold"}>
          {difficultyLabel[question.difficulty] || question.difficulty}
        </Tag>
        <Tag>{question.subject_name || "未分科"}</Tag>
        <Tag>{question.chapter_name || "未分章"}</Tag>
        <Tag>{question.knowledge_point_name || "未标知识点"}</Tag>
      </div>
      <Typography.Title level={4} className="question-viewer__stem">
        {question.stem}
      </Typography.Title>
      {question.stem_image_url ? <Image className="question-viewer__image" src={question.stem_image_url} /> : null}
      <Form layout="vertical">
        <Form.Item>{renderInput()}</Form.Item>
      </Form>
      <div className="question-viewer__actions">
        <Space wrap>
          {onSubmit ? (
            <Button type="primary" icon={<Flag size={16} />} onClick={onSubmit} disabled={!selected || submitted}>
              提交答案
            </Button>
          ) : null}
          {onFavorite ? (
            <Button icon={<Heart size={16} fill={question.is_favorited ? "currentColor" : "none"} />} onClick={onFavorite}>
              {question.is_favorited ? "取消收藏" : "收藏"}
            </Button>
          ) : null}
          {onFeedback ? (
            <Button icon={<MessageSquareWarning size={16} />} onClick={onFeedback}>
              反馈纠错
            </Button>
          ) : null}
        </Space>
      </div>
      {submitted ? (
        <div className="question-analysis">
          <div>
            <Typography.Text strong>正确答案：</Typography.Text>
            <Typography.Text>{correct}</Typography.Text>
          </div>
          <div>
            <Typography.Text strong>解析：</Typography.Text>
            <Typography.Paragraph>{analysis || question.analysis}</Typography.Paragraph>
          </div>
          {question.analysis_image_url ? <Image src={question.analysis_image_url} width={220} /> : null}
        </div>
      ) : null}
    </div>
  );
}