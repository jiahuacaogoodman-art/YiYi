export const difficultyLabel: Record<string, string> = {
  easy: "简单",
  medium: "中等",
  hard: "困难",
};

export const questionTypeLabel: Record<string, string> = {
  single_choice: "单选题",
  multiple_choice: "多选题",
  true_false: "判断题",
  fill_blank: "填空题",
  short_answer: "简答题",
};

export const statusLabel: Record<string, string> = {
  draft: "草稿",
  pending_review: "待审核",
  published: "已发布",
  offline: "已下架",
  pending: "待处理",
  processing: "处理中",
  resolved: "已处理",
  ignored: "已忽略",
  completed: "已完成",
  failed: "失败",
  previewed: "已预览",
};

export function percent(value?: number | null) {
  return `${Number(value || 0).toFixed(1).replace(".0", "")}%`;
}

export function shortDate(value?: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function truncate(text: string, length = 64) {
  if (text.length <= length) return text;
  return `${text.slice(0, length)}...`;
}

export function compactNumber(value?: number | null) {
  return Number(value || 0).toLocaleString("zh-CN");
}