import { Card, Empty, Space, Typography } from "antd";
import { ThumbsUp } from "lucide-react";
import { useEffect, useState } from "react";
import { interactionApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import { useQuestionInteractions } from "../../hooks/useQuestionInteractions";
import type { Question } from "../../types/domain";

export function LikesPage() {
  const [items, setItems] = useState<Question[]>([]);
  const interactions = useQuestionInteractions({
    onQuestionPatch: (questionId, patch) => {
      setItems((current) => current.map((item) => (item.id === questionId ? { ...item, ...patch } : item)));
    },
  });

  const load = () => interactionApi.myLikes({ page_size: 100 }).then((data) => setItems(data.items));

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="page">
      <div className="page-heading page-heading--hero">
        <div>
          <span className="page-heading__eyebrow">认可题目</span>
          <Typography.Title level={2}>我的点赞</Typography.Title>
          <Typography.Text type="secondary">集中查看你点过赞的题目，快速回到高价值讨论和解析。</Typography.Text>
        </div>
        <span className="page-heading__badge"><ThumbsUp size={18} /> {items.length} 道题</span>
      </div>
      <Space direction="vertical" size={16} className="full-width section-row">
        {items.length ? (
          items.map((item) => (
            <Card key={item.id} variant="borderless">
              <QuestionViewer
                question={item}
                submitted
                onNote={() => interactions.openNotes(item)}
                onComment={() => interactions.openComments(item)}
                onLike={() => interactions.toggleLike(item)}
              />
            </Card>
          ))
        ) : (
          <div className="panel">
            <Empty description="还没有点赞，遇到有帮助的题目可以点个赞" />
          </div>
        )}
      </Space>
      {interactions.modals}
    </div>
  );
}