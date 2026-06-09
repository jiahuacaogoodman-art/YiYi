import { http, unwrap } from "./http";
import type {
  Chapter,
  DashboardStatistics,
  Exam,
  ExamRecord,
  ExamStart,
  Feedback,
  ImportPreview,
  ImportRecord,
  KnowledgePoint,
  LikeStatus,
  PageOut,
  PracticeAnswerResult,
  PracticeStart,
  QuestionComment,
  QuestionNote,
  Question,
  Subject,
  SystemSetting,
  User,
  UserStatistics,
  WrongQuestion,
} from "../types/domain";

export interface QueryParams {
  [key: string]: string | number | boolean | undefined | null;
}

export const authApi = {
  login: (payload: { username: string; password: string }) =>
    unwrap<{ access_token: string; token_type: string }>(http.post("/auth/login", payload)),
  register: (payload: { username: string; password: string; nickname?: string; email: string; phone?: string }) =>
    unwrap<User>(http.post("/auth/register", payload)),
  me: () => unwrap<User>(http.get("/auth/me")),
  logout: () => unwrap<{ message: string }>(http.post("/auth/logout")),
};

export const taxonomyApi = {
  subjects: (params?: QueryParams) => unwrap<PageOut<Subject>>(http.get("/subjects", { params })),
  chapters: (params?: QueryParams) => unwrap<PageOut<Chapter>>(http.get("/chapters", { params })),
  knowledgePoints: (params?: QueryParams) => unwrap<PageOut<KnowledgePoint>>(http.get("/knowledge-points", { params })),
  createSubject: (payload: Partial<Subject>) => unwrap<Subject>(http.post("/admin/subjects", payload)),
  updateSubject: (id: number, payload: Partial<Subject>) => unwrap<Subject>(http.put(`/admin/subjects/${id}`, payload)),
  deleteSubject: (id: number) => unwrap<{ message: string }>(http.delete(`/admin/subjects/${id}`)),
  reorderSubjects: (payload: Array<{ id: number; sort_order: number }>) =>
    unwrap<{ message: string }>(http.post("/admin/subjects/reorder", payload)),
  createChapter: (payload: Partial<Chapter>) => unwrap<Chapter>(http.post("/admin/chapters", payload)),
  updateChapter: (id: number, payload: Partial<Chapter>) => unwrap<Chapter>(http.put(`/admin/chapters/${id}`, payload)),
  deleteChapter: (id: number) => unwrap<{ message: string }>(http.delete(`/admin/chapters/${id}`)),
  batchChapterStatus: (payload: { ids: number[]; is_enabled: boolean }) =>
    unwrap<{ message: string }>(http.post("/admin/chapters/batch-status", payload)),
  createKnowledgePoint: (payload: Partial<KnowledgePoint>) =>
    unwrap<KnowledgePoint>(http.post("/admin/knowledge-points", payload)),
  updateKnowledgePoint: (id: number, payload: Partial<KnowledgePoint>) =>
    unwrap<KnowledgePoint>(http.put(`/admin/knowledge-points/${id}`, payload)),
  deleteKnowledgePoint: (id: number) => unwrap<{ message: string }>(http.delete(`/admin/knowledge-points/${id}`)),
  importKnowledgePoints: (payload: Array<Record<string, unknown>>) =>
    unwrap<{ message: string }>(http.post("/admin/knowledge-points/import", payload)),
};

export const questionApi = {
  list: (params?: QueryParams) => unwrap<PageOut<Question>>(http.get("/questions", { params })),
  detail: (id: number) => unwrap<Question>(http.get(`/questions/${id}`)),
  create: (payload: Partial<Question>) => unwrap<Question>(http.post("/admin/questions", payload)),
  update: (id: number, payload: Partial<Question>) => unwrap<Question>(http.put(`/admin/questions/${id}`, payload)),
  delete: (id: number) => unwrap<{ message: string }>(http.delete(`/admin/questions/${id}`)),
  restore: (id: number) => unwrap<{ message: string }>(http.post(`/admin/questions/${id}/restore`)),
  hardDelete: (id: number) => unwrap<{ message: string }>(http.delete(`/admin/questions/${id}/hard`)),
  batch: (payload: { ids: number[]; action: string; [key: string]: unknown }) =>
    unwrap<{ message: string }>(http.post("/admin/questions/batch", payload)),
  duplicate: (payload: { stem: string; threshold?: number }) =>
    unwrap<Array<Record<string, unknown>>>(http.post("/admin/questions/check-duplicate", payload)),
  favorite: (id: number) => unwrap<{ message: string }>(http.post(`/questions/${id}/favorite`)),
  unfavorite: (id: number) => unwrap<{ message: string }>(http.delete(`/questions/${id}/favorite`)),
  feedback: (id: number, payload: { feedback_type: string; content: string }) =>
    unwrap<Feedback>(http.post(`/questions/${id}/feedback`, payload)),
  importPreview: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return unwrap<ImportPreview>(http.post("/admin/questions/import/preview", form));
  },
  importConfirm: (payload: { import_record_id: number; auto_create_taxonomy: boolean; skip_duplicates: boolean }) =>
    unwrap<ImportRecord>(http.post("/admin/questions/import/confirm", payload)),
  importRecords: (params?: QueryParams) => unwrap<PageOut<ImportRecord>>(http.get("/admin/questions/import/records", { params })),
  downloadTemplate: () =>
    unwrap<Blob>(
      http.get("/admin/questions/import/template", {
        responseType: "blob",
      }),
    ),
  exportQuestions: (params?: QueryParams) =>
    unwrap<Blob>(
      http.get("/admin/questions/export", {
        params,
        responseType: "blob",
      }),
    ),
  uploadImage: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return unwrap<{ url: string; file_name: string; size: number }>(http.post("/admin/upload/image", form));
  },
};

export const practiceApi = {
  start: (payload: { mode: string; subject_id?: number; chapter_id?: number; knowledge_point_id?: number; question_count?: number }) =>
    unwrap<PracticeStart>(http.post("/practice/start", payload)),
  answer: (payload: { question_id: number; answer: string; mode?: string; time_spent_seconds?: number }) =>
    unwrap<PracticeAnswerResult>(http.post("/practice/answer", payload)),
  wrong: (params?: QueryParams) => unwrap<PageOut<WrongQuestion>>(http.get("/practice/wrong", { params })),
  removeWrong: (questionId: number) => unwrap<{ message: string }>(http.delete(`/practice/wrong/${questionId}`)),
  favorites: (params?: QueryParams) => unwrap<PageOut<Question>>(http.get("/practice/favorites", { params })),
};

export const interactionApi = {
  questionNotes: (questionId: number, params?: QueryParams) =>
    unwrap<PageOut<QuestionNote>>(http.get(`/questions/${questionId}/notes`, { params })),
  createNote: (questionId: number, payload: { content: string }) =>
    unwrap<QuestionNote>(http.post(`/questions/${questionId}/notes`, payload)),
  updateNote: (noteId: number, payload: { content: string }) => unwrap<QuestionNote>(http.put(`/notes/${noteId}`, payload)),
  deleteNote: (noteId: number) => unwrap<{ message: string }>(http.delete(`/notes/${noteId}`)),
  myNotes: (params?: QueryParams) => unwrap<PageOut<QuestionNote>>(http.get("/me/notes", { params })),

  questionComments: (questionId: number, params?: QueryParams) =>
    unwrap<PageOut<QuestionComment>>(http.get(`/questions/${questionId}/comments`, { params })),
  createComment: (questionId: number, payload: { content: string }) =>
    unwrap<QuestionComment>(http.post(`/questions/${questionId}/comments`, payload)),
  updateComment: (commentId: number, payload: { content: string }) =>
    unwrap<QuestionComment>(http.put(`/comments/${commentId}`, payload)),
  deleteComment: (commentId: number) => unwrap<{ message: string }>(http.delete(`/comments/${commentId}`)),
  myComments: (params?: QueryParams) => unwrap<PageOut<QuestionComment>>(http.get("/me/comments", { params })),

  likeStatus: (questionId: number) => unwrap<LikeStatus>(http.get(`/questions/${questionId}/like`)),
  like: (questionId: number) => unwrap<LikeStatus>(http.post(`/questions/${questionId}/like`)),
  unlike: (questionId: number) => unwrap<LikeStatus>(http.delete(`/questions/${questionId}/like`)),
  myLikes: (params?: QueryParams) => unwrap<PageOut<Question>>(http.get("/me/likes", { params })),
};

export const examApi = {
  publicList: (params?: QueryParams) => unwrap<PageOut<Exam>>(http.get("/exams", { params })),
  detail: (id: number) => unwrap<Exam>(http.get(`/exams/${id}`)),
  start: (id: number) => unwrap<ExamStart>(http.post(`/exams/${id}/start`)),
  submit: (id: number, payload: { record_id: number; answers: Array<{ question_id: number; answer: string }> }) =>
    unwrap<ExamRecord>(http.post(`/exams/${id}/submit`, payload)),
  record: (id: number) => unwrap<ExamRecord>(http.get(`/exams/records/${id}`)),
  adminList: (params?: QueryParams) => unwrap<PageOut<Exam>>(http.get("/admin/exams", { params })),
  create: (payload: Partial<Exam> & { questions?: Array<{ question_id: number; score: number; sort_order: number }> }) =>
    unwrap<Exam>(http.post("/admin/exams", payload)),
  update: (id: number, payload: Partial<Exam>) => unwrap<Exam>(http.put(`/admin/exams/${id}`, payload)),
  autoGenerate: (payload: Record<string, unknown>) => unwrap<Exam>(http.post("/admin/exams/auto-generate", payload)),
  publish: (id: number) => unwrap<{ message: string }>(http.post(`/admin/exams/${id}/publish`)),
  offline: (id: number) => unwrap<{ message: string }>(http.post(`/admin/exams/${id}/offline`)),
  statistics: (id: number) => unwrap<Record<string, unknown>>(http.get(`/admin/exams/${id}/statistics`)),
};

export const statisticsApi = {
  user: () => unwrap<UserStatistics>(http.get("/statistics/user")),
  dashboard: () => unwrap<DashboardStatistics>(http.get("/admin/statistics/dashboard")),
};

export const adminApi = {
  users: (params?: QueryParams) => unwrap<PageOut<User>>(http.get("/admin/users", { params })),
  createAdminUser: (payload: Record<string, unknown>) => unwrap<User>(http.post("/admin/users", payload)),
  updateUserStatus: (id: number, payload: { is_active: boolean }) =>
    unwrap<{ message: string }>(http.put(`/admin/users/${id}/status`, payload)),
  resetPassword: (id: number, payload: { new_password: string }) =>
    unwrap<{ message: string }>(http.post(`/admin/users/${id}/reset-password`, payload)),
  feedback: (params?: QueryParams) => unwrap<PageOut<Feedback>>(http.get("/admin/feedback", { params })),
  updateFeedback: (id: number, payload: { status: string; handler_note?: string }) =>
    unwrap<Feedback>(http.put(`/admin/feedback/${id}`, payload)),
  logs: (params?: QueryParams) => unwrap<PageOut<Record<string, unknown>>>(http.get("/admin/logs", { params })),
  settings: () => unwrap<SystemSetting[]>(http.get("/admin/settings")),
  updateSetting: (key: string, payload: { value: string; description?: string; is_public?: boolean }) =>
    unwrap<SystemSetting>(http.put(`/admin/settings/${key}`, payload)),
};