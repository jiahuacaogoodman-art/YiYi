import { ConfigProvider, App as AntApp } from "antd";
import zhCN from "antd/locale/zh_CN";
import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { StudentShell } from "./layouts/StudentShell";
import { AdminShell } from "./layouts/AdminShell";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { useAuthStore } from "./stores/authStore";
import { LoginPage } from "./pages/LoginPage";
import { HomePage } from "./pages/student/HomePage";
import { SubjectsPage } from "./pages/student/SubjectsPage";
import { PracticePage } from "./pages/student/PracticePage";
import { WrongBookPage } from "./pages/student/WrongBookPage";
import { FavoritesPage } from "./pages/student/FavoritesPage";
import { NotesPage } from "./pages/student/NotesPage";
import { CommentsPage } from "./pages/student/CommentsPage";
import { LikesPage } from "./pages/student/LikesPage";
import { ExamsPage } from "./pages/student/ExamsPage";
import { StatisticsPage } from "./pages/student/StatisticsPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { TaxonomyManagePage } from "./pages/admin/TaxonomyManagePage";
import { QuestionsManagePage } from "./pages/admin/QuestionsManagePage";
import { QuestionImportPage } from "./pages/admin/QuestionImportPage";
import { ExamsManagePage } from "./pages/admin/ExamsManagePage";
import { UsersManagePage } from "./pages/admin/UsersManagePage";
import { FeedbackManagePage } from "./pages/admin/FeedbackManagePage";
import { AdminStatisticsPage } from "./pages/admin/AdminStatisticsPage";
import { LogsPage } from "./pages/admin/LogsPage";
import { SettingsPage } from "./pages/admin/SettingsPage";

export function App() {
  const bootstrap = useAuthStore((state) => state.bootstrap);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: "#4c7dff",
          colorSuccess: "#16b873",
          colorWarning: "#ff9f2d",
          colorError: "#f04b4b",
          colorInfo: "#4c7dff",
          colorText: "#1d2636",
          colorTextSecondary: "#8a94a6",
          colorBgLayout: "#f5f8ff",
          colorBgContainer: "#ffffff",
          colorBorder: "#e8edf6",
          borderRadius: 10,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        components: {
          Card: { borderRadiusLG: 12 },
          Button: {
            borderRadius: 10,
            controlHeight: 36,
            primaryShadow: "0 12px 28px rgba(76, 125, 255, 0.22)",
          },
          Layout: { siderBg: "#ffffff", bodyBg: "#f5f8ff" },
          Menu: {
            itemBorderRadius: 10,
            itemSelectedBg: "#eff5ff",
            itemSelectedColor: "#4c7dff",
            itemColor: "#6f7a8e",
            itemHoverColor: "#4c7dff",
            itemHoverBg: "#f6f9ff",
          },
          Segmented: {
            itemSelectedBg: "#4c7dff",
            itemSelectedColor: "#ffffff",
          },
          Table: {
            headerBg: "#f6f9ff",
            headerColor: "#455066",
            rowHoverBg: "#f8fbff",
          },
          Progress: {
            defaultColor: "#4c7dff",
            remainingColor: "#edf2fb",
          },
        },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<StudentShell />}>
                <Route index element={<HomePage />} />
                <Route path="subjects" element={<SubjectsPage />} />
                <Route path="practice" element={<PracticePage />} />
                <Route path="wrong" element={<WrongBookPage />} />
                <Route path="favorites" element={<FavoritesPage />} />
                <Route path="notes" element={<NotesPage />} />
                <Route path="comments" element={<CommentsPage />} />
                <Route path="likes" element={<LikesPage />} />
                <Route path="exams" element={<ExamsPage />} />
                <Route path="statistics" element={<StatisticsPage />} />
              </Route>
            </Route>
            <Route element={<ProtectedRoute adminOnly />}>
              <Route element={<AdminShell />}>
                <Route path="admin" element={<AdminDashboardPage />} />
                <Route path="admin/questions" element={<QuestionsManagePage />} />
                <Route path="admin/import" element={<QuestionImportPage />} />
                <Route path="admin/subjects" element={<TaxonomyManagePage />} />
                <Route path="admin/chapters" element={<TaxonomyManagePage />} />
                <Route path="admin/knowledge-points" element={<TaxonomyManagePage />} />
                <Route path="admin/taxonomy" element={<Navigate to="/admin/subjects" replace />} />
                <Route path="admin/exams" element={<ExamsManagePage />} />
                <Route path="admin/users" element={<UsersManagePage />} />
                <Route path="admin/feedback" element={<FeedbackManagePage />} />
                <Route path="admin/statistics" element={<AdminStatisticsPage />} />
                <Route path="admin/logs" element={<LogsPage />} />
                <Route path="admin/settings" element={<SettingsPage />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
}