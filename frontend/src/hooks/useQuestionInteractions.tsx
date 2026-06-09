import { Button, Empty, Input, Modal, Space, Typography, message } from "antd";
import { useState } from "react";
import { interactionApi } from "../api/client";
import type { Question, QuestionComment, QuestionNote } from "../types/domain";

interface UseQuestionInteractionsOptions {
  onQuestionPatch?: (questionId: number, patch: Partial<Question>) => void;
}

export function useQuestionInteractions(options: UseQuestionInteractionsOptions = {}) {
  const [noteQuestion, setNoteQuestion] = useState<Question | null>(null);
  const [notes, setNotes] = useState<QuestionNote[]>([]);
  const [noteText, setNoteText] = useState("");
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [commentQuestion, setCommentQuestion] = useState<Question | null>(null);
  const [comments, setComments] = useState<QuestionComment[]>([]);
  const [commentText, setCommentText] = useState("");
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);

  const patchQuestion = (questionId: number, patch: Partial<Question>) => {
    options.onQuestionPatch?.(questionId, patch);
  };

  const openNotes = async (question: Question) => {
    const data = await interactionApi.questionNotes(question.id, { page_size: 100 });
    setNoteQuestion(question);
    setNotes(data.items);
    setNoteText("");
    setEditingNoteId(null);
  };

  const saveNote = async () => {
    if (!noteQuestion || !noteText.trim()) return;
    if (editingNoteId) {
      const updated = await interactionApi.updateNote(editingNoteId, { content: noteText.trim() });
      setNotes((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      message.success("笔记已更新");
    } else {
      const created = await interactionApi.createNote(noteQuestion.id, { content: noteText.trim() });
      const nextCount = notes.length + 1;
      setNotes((items) => [created, ...items]);
      patchQuestion(noteQuestion.id, { note_count: nextCount });
      message.success("笔记已保存");
    }
    setNoteText("");
    setEditingNoteId(null);
  };

  const deleteNote = async (noteId: number) => {
    if (!noteQuestion) return;
    await interactionApi.deleteNote(noteId);
    const nextCount = Math.max(notes.length - 1, 0);
    setNotes((items) => items.filter((item) => item.id !== noteId));
    patchQuestion(noteQuestion.id, { note_count: nextCount });
    message.success("笔记已删除");
  };

  const openComments = async (question: Question) => {
    const data = await interactionApi.questionComments(question.id, { page_size: 100 });
    setCommentQuestion(question);
    setComments(data.items);
    setCommentText("");
    setEditingCommentId(null);
  };

  const saveComment = async () => {
    if (!commentQuestion || !commentText.trim()) return;
    if (editingCommentId) {
      const updated = await interactionApi.updateComment(editingCommentId, { content: commentText.trim() });
      setComments((items) => items.map((item) => (item.id === updated.id ? updated : item)));
      message.success("评论已更新");
    } else {
      const created = await interactionApi.createComment(commentQuestion.id, { content: commentText.trim() });
      const nextCount = comments.length + 1;
      setComments((items) => [created, ...items]);
      patchQuestion(commentQuestion.id, { comment_count: nextCount });
      message.success("评论已发布");
    }
    setCommentText("");
    setEditingCommentId(null);
  };

  const deleteComment = async (commentId: number) => {
    if (!commentQuestion) return;
    await interactionApi.deleteComment(commentId);
    const nextCount = Math.max(comments.length - 1, 0);
    setComments((items) => items.filter((item) => item.id !== commentId));
    patchQuestion(commentQuestion.id, { comment_count: nextCount });
    message.success("评论已删除");
  };

  const toggleLike = async (question: Question) => {
    const status = question.is_liked ? await interactionApi.unlike(question.id) : await interactionApi.like(question.id);
    patchQuestion(question.id, { is_liked: status.is_liked, like_count: status.like_count });
  };

  const modals = (
    <>
      <Modal
        title="题目笔记"
        open={Boolean(noteQuestion)}
        onOk={saveNote}
        onCancel={() => setNoteQuestion(null)}
        okText={editingNoteId ? "更新笔记" : "保存笔记"}
        width={720}
      >
        <Input.TextArea
          rows={4}
          value={noteText}
          onChange={(event) => setNoteText(event.target.value)}
          placeholder="写下这道题的记忆点、易错点或复盘思路"
        />
        <Space direction="vertical" size={12} className="interaction-list">
          {notes.length ? (
            notes.map((note) => (
              <div className="interaction-item" key={note.id}>
                <Typography.Paragraph>{note.content}</Typography.Paragraph>
                <Space>
                  <Button
                    size="small"
                    onClick={() => {
                      setEditingNoteId(note.id);
                      setNoteText(note.content);
                    }}
                  >
                    编辑
                  </Button>
                  <Button size="small" danger onClick={() => deleteNote(note.id)}>
                    删除
                  </Button>
                </Space>
              </div>
            ))
          ) : (
            <Empty description="还没有笔记" />
          )}
        </Space>
      </Modal>
      <Modal
        title="题目评论"
        open={Boolean(commentQuestion)}
        onOk={saveComment}
        onCancel={() => setCommentQuestion(null)}
        okText={editingCommentId ? "更新评论" : "发布评论"}
        width={760}
      >
        <Input.TextArea
          rows={4}
          value={commentText}
          onChange={(event) => setCommentText(event.target.value)}
          placeholder="写下你的理解、提问或补充说明"
        />
        <Space direction="vertical" size={12} className="interaction-list">
          {comments.length ? (
            comments.map((comment) => (
              <div className="interaction-item" key={comment.id}>
                <div className="interaction-item__head">
                  <strong>{comment.nickname || comment.username}</strong>
                  <Typography.Text type="secondary">
                    {new Date(comment.created_at).toLocaleString("zh-CN", { hour12: false })}
                  </Typography.Text>
                </div>
                <Typography.Paragraph>{comment.content}</Typography.Paragraph>
                {comment.is_mine ? (
                  <Space>
                    <Button
                      size="small"
                      onClick={() => {
                        setEditingCommentId(comment.id);
                        setCommentText(comment.content);
                      }}
                    >
                      编辑
                    </Button>
                    <Button size="small" danger onClick={() => deleteComment(comment.id)}>
                      删除
                    </Button>
                  </Space>
                ) : null}
              </div>
            ))
          ) : (
            <Empty description="还没有评论" />
          )}
        </Space>
      </Modal>
    </>
  );

  return {
    modals,
    openNotes,
    openComments,
    toggleLike,
  };
}