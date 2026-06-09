import { Card, Empty, Space, Typography } from "antd";
import { NotebookPen } from "lucide-react";
import { useEffect, useState } from "react";
import { interactionApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import { useQuestionInteractions } from "../../hooks/useQuestionInteractions";
import type { QuestionNote } from "../../types/domain";

export function NotesPage() {
  const [items, setItems] = useState<QuestionNote[]>([]);
  const interactions = useQuestionInteractions({
    onQuestionPatch: (questionId, patch) => {
      setItems((current) =>
        current.map((item) => (item.question?.id === questionId ? { ...item, question: { ...item.question, ...patch } } : item)),
      );
    },
  });

  const load = () => interactionApi.myNotes({ page_size: 100 }).then((data) => setItems(data.items));

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="page">
      <div className="page-heading page-heading--hero">
        <div>
          <span className="page-heading__eyebrow">复盘记录</span>
          <Typography.Title level={2}>我的笔记</Typography.Title>
          <Typography.Text type="secondary">集中查看你在题目上写下的记忆点、易错点和复盘思路。</Typography.Text>
        </div>
        <span className="page-heading__badge"><NotebookPen size={18} /> {items.length} 条笔记</span>
      </div>
      <Space direction="vertical" size={16} className="full-width section-row">
        {items.length ? (
          items.map((item) => (
            <Card key={item.id} variant="borderless">
              <div className="interaction-note-preview">
                <Typography.Text type="secondary">笔记</Typography.Text>
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
            <Empty description="还没有笔记，刷题时可以给重点题写复盘" />
          </div>
        )}
      </Space>
      {interactions.modals}
    </div>
  );
}