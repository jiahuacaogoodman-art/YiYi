import { Button, Checkbox, Form, Image, Input, Radio, Space, Tag, Typography } from "antd";
import { Flag, Heart, MessageSquare, MessageSquareWarning, NotebookPen, ThumbsUp } from "lucide-react";
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
  onNote?: () => void;
  onComment?: () => void;
  onLike?: () => void;
  isLiked?: boolean;
  noteCount?: number;
  commentCount?: number;
  likeCount?: number;
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
  onNote,
  onComment,
  onLike,
  isLiked,
  noteCount,
  commentCount,
  likeCount,
}: QuestionViewerProps) {
  const type = question.question_type;
  const selected = value || "";
  const correct = correctAnswer || question.correct_answer;
  const hasSelectedAnswer = Boolean(selected);
  const selectedSet = new Set(selected.split(",").filter(Boolean));
  const correctSet = new Set(correct.split(",").filter(Boolean));

  const optionClassName = (key: string) =>
    [
      "answer-option",
      selectedSet.has(key) ? "answer-option--selected" : "",
      submitted && correctSet.has(key) ? "answer-option--correct" : "",
      submitted && selectedSet.has(key) && !correctSet.has(key) ? "answer-option--wrong" : "",
    ]
      .filter(Boolean)
      .join(" ");

  const renderInput = () => {
    if (type === "single_choice" || type === "true_false") {
      return (
        <Radio.Group className="answer-options" value={selected} onChange={(event) => onChange?.(event.target.value)}>
          <Space direction="vertical" size={10}>
            {(question.options || []).map((option) => (
              <Radio key={option.option_key} value={option.option_key} className={optionClassName(option.option_key)}>
                <span className="answer-option__key">{option.option_key}</span>
                <span className="answer-option__content">{option.content}</span>
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
              <Checkbox key={option.option_key} value={option.option_key} className={optionClassName(option.option_key)}>
                <span className="answer-option__key">{option.option_key}</span>
                <span className="answer-option__content">{option.content}</span>
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
        <Tag className="question-tag question-tag--type">{questionTypeLabel[type] || type}</Tag>
        <Tag color={question.difficulty === "hard" ? "red" : question.difficulty === "easy" ? "green" : "gold"}>
          {difficultyLabel[question.difficulty] || question.difficulty}
        </Tag>
        <Tag className="question-tag">{question.subject_name || "未分科"}</Tag>
        <Tag className="question-tag">{question.chapter_name || "未分章"}</Tag>
        <Tag className="question-tag">{question.knowledge_point_name || "未标知识点"}</Tag>
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
          {onNote ? (
            <Button icon={<NotebookPen size={16} />} onClick={onNote}>
              笔记 {noteCount ?? question.note_count ?? 0}
            </Button>
          ) : null}
          {onComment ? (
            <Button icon={<MessageSquare size={16} />} onClick={onComment}>
              评论 {commentCount ?? question.comment_count ?? 0}
            </Button>
          ) : null}
          {onLike ? (
            <Button icon={<ThumbsUp size={16} fill={(isLiked ?? question.is_liked) ? "currentColor" : "none"} />} onClick={onLike}>
              点赞 {likeCount ?? question.like_count ?? 0}
            </Button>
          ) : null}
        </Space>
      </div>
      {submitted ? (
        <div className="question-analysis">
          <div className={hasSelectedAnswer ? "question-analysis__summary" : "question-analysis__summary question-analysis__summary--single"}>
            <span>
              <Typography.Text strong>正确答案：</Typography.Text>
              <b>{correct}</b>
            </span>
            {hasSelectedAnswer ? (
              <span>
                <Typography.Text strong>你的答案：</Typography.Text>
                <b className={selected === correct ? "is-correct" : "is-wrong"}>{selected}</b>
              </span>
            ) : null}
          </div>
          <div className="question-analysis__block">
            <Typography.Text strong className="question-analysis__title">解析</Typography.Text>
            <Typography.Paragraph>{analysis || question.analysis}</Typography.Paragraph>
          </div>
          {question.analysis_image_url ? <Image src={question.analysis_image_url} width={220} /> : null}
        </div>
      ) : null}
    </div>
  );
}