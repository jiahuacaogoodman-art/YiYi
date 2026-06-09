import { Card, Empty, Space, Typography } from "antd";
import { MessageSquare } from "lucide-react";
import { useEffect, useState } from "react";
import { interactionApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import { useQuestionInteractions } from "../../hooks/useQuestionInteractions";
import type { QuestionComment } from "../../types/domain";

export function CommentsPage() {
  const [items, setItems] = useState<QuestionComment[]>([]);
  const interactions = useQuestionInteractions({
    onQuestionPatch: (questionId, patch) => {
      setItems((current) =>
        current.map((item) => (item.question?.id === questionId ? { ...item, question: { ...item.question, ...patch } } : item)),
      );
    },
  });

  const load = () => interactionApi.myComments({ page_size: 100 }).then((data) => setItems(data.items));

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="page">
      <div className="page-heading page-heading--hero">
        <div>
          <span className="page-heading__eyebrow">讨论记录</span>
          <Typography.Title level={2}>我的评论</Typography.Title>
          <Typography.Text type="secondary">查看你在题目下发布过的讨论、提问和补充说明。</Typography.Text>
        </div>
        <span className="page-heading__badge"><MessageSquare size={18} /> {items.length} 条评论</span>
      </div>
      <Space direction="vertical" size={16} className="full-width section-row">
        {items.length ? (
          items.map((item) => (
            <Card key={item.id} variant="borderless">
              <div className="interaction-note-preview">
                <Typography.Text type="secondary">评论</Typography.Text>
                <Typography.Paragraph>{item.content}</Typography.Paragraph>
              </div>
              {item.question ? (
                <QuestionViewer
                  question={item.question}
                  submitted
                  onNote={() => interactions.openNotes(item.question!)}
                  onComment={() => interactions.openComments(item.question!)}
                  onLike={() => interactions.toggleLike(item.question!)}
                />
              ) : null}
            </Card>
          ))
        ) : (
          <div className="panel">
            <Empty description="还没有评论，打开题目评论区参与讨论" />
          </div>
        )}
      </Space>
      {interactions.modals}
    </div>
  );
}