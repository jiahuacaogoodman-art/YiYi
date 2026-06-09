export interface PageOut<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface Role {
  id: number;
  name: "student" | "admin" | "super_admin" | string;
  label: string;
}

export interface User {
  id: number;
  username: string;
  nickname: string;
  email?: string | null;
  phone?: string | null;
  role: Role;
  is_active: boolean;
  last_login_at?: string | null;
  created_at: string;
  total_answers?: number;
  correct_rate?: number;
  wrong_count?: number;
  favorite_count?: number;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  icon?: string | null;
  sort_order: number;
  is_enabled: boolean;
  description?: string | null;
  question_count: number;
  practiced_count: number;
  correct_rate: number;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  subject_id: number;
  subject_name?: string | null;
  name: string;
  code: string;
  sort_order: number;
  is_enabled: boolean;
  description?: string | null;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgePoint {
  id: number;
  subject_id: number;
  chapter_id: number;
  subject_name?: string | null;
  chapter_name?: string | null;
  name: string;
  label?: string | null;
  importance_level: string;
  description?: string | null;
  sort_order: number;
  is_enabled: boolean;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface QuestionOption {
  id?: number;
  option_key: string;
  content: string;
  image_url?: string | null;
  sort_order: number;
}

export interface Question {
  id: number;
  stem: string;
  question_type: string;
  correct_answer: string;
  analysis: string;
  subject_id: number;
  chapter_id: number;
  knowledge_point_id: number;
  subject_name?: string | null;
  chapter_name?: string | null;
  knowledge_point_name?: string | null;
  difficulty: string;
  importance: string;
  source: string;
  year?: number | null;
  school?: string | null;
  has_image: boolean;
  stem_image_url?: string | null;
  analysis_image_url?: string | null;
  status: string;
  practice_count: number;
  correct_count?: number;
  wrong_count?: number;
  correct_rate: number;
  favorite_count: number;
  feedback_count: number;
  options?: QuestionOption[];
  tags: string[];
  is_favorited?: boolean;
  created_at: string;
  updated_at: string;
}

export interface PracticeStart {
  mode: string;
  total: number;
  questions: Question[];
}

export interface PracticeAnswerResult {
  question_id: number;
  is_correct: boolean;
  correct_answer: string;
  analysis: string;
  added_to_wrong_book: boolean;
  wrong_count: number;
  question_stat: {
    practice_count: number;
    correct_count: number;
    wrong_count: number;
    correct_rate: number;
  };
}

export interface WrongQuestion {
  id: number;
  question: Question;
  wrong_count: number;
  last_wrong_at?: string | null;
  last_answer_correct: boolean;
}

export interface Exam {
  id: number;
  name: string;
  exam_type: string;
  subject_id?: number | null;
  subject_name?: string | null;
  total_score: number;
  pass_score: number;
  duration_minutes: number;
  is_public: boolean;
  status: string;
  description?: string | null;
  question_count: number;
  questions?: Question[];
  created_at: string;
  updated_at: string;
}

export interface ExamStart {
  record_id: number;
  exam: Exam;
  started_at: string;
  deadline_at: string;
}

export interface ExamRecord {
  id: number;
  exam_id: number;
  exam_name?: string | null;
  user_id: number;
  started_at: string;
  submitted_at?: string | null;
  score?: number | null;
  correct_count: number;
  wrong_count: number;
  status: string;
  answers: Array<Record<string, unknown>>;
}

export interface UserStatistics {
  total_answers: number;
  correct_count: number;
  wrong_count: number;
  correct_rate: number;
  subject_accuracy: Array<Record<string, unknown>>;
  chapter_mastery: Array<Record<string, unknown>>;
  recent_7_days: Array<Record<string, unknown>>;
  high_frequency_wrong_points: Array<Record<string, unknown>>;
  recommended_chapters: Array<Record<string, unknown>>;
}

export interface DashboardStatistics {
  total_questions: number;
  published_questions: number;
  draft_questions: number;
  pending_review_questions: number;
  today_new_questions: number;
  total_users: number;
  today_practice_count: number;
  feedback_count: number;
  subject_distribution: Array<Record<string, unknown>>;
  user_practice_trend: Array<Record<string, unknown>>;
  top_wrong_knowledge_points: Array<Record<string, unknown>>;
  recent_import_records: Array<Record<string, unknown>>;
  recent_operation_logs: Array<Record<string, unknown>>;
}

export interface Feedback {
  id: number;
  question_id: number;
  user_id: number;
  feedback_type: string;
  content: string;
  status: string;
  handler_id?: number | null;
  handled_at?: string | null;
  handler_note?: string | null;
  created_at: string;
}

export interface SystemSetting {
  id: number;
  key: string;
  value: string;
  description?: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface ImportPreview {
  import_record_id: number;
  total_count: number;
  valid_count: number;
  failed_count: number;
  duplicate_count: number;
  rows: Array<Record<string, unknown>>;
}

export interface ImportRecord {
  id: number;
  file_name: string;
  status: string;
  total_count: number;
  success_count: number;
  failed_count: number;
  skipped_count: number;
  duplicate_count: number;
  error_report_path?: string | null;
  created_at: string;
}