import { ConfigProvider, App as AntApp } from "antd";
import zhCN from "antd/locale/zh_CN";
import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./layouts/AppShell";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { useAuthStore } from "./stores/authStore";
import { LoginPage } from "./pages/LoginPage";
import { HomePage } from "./pages/student/HomePage";
import { SubjectsPage } from "./pages/student/SubjectsPage";
import { PracticePage } from "./pages/student/PracticePage";
import { WrongBookPage } from "./pages/student/WrongBookPage";
import { FavoritesPage } from "./pages/student/FavoritesPage";
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
          colorPrimary: "#183f38",
          colorSuccess: "#2f8f62",
          colorWarning: "#b98538",
          colorError: "#d74f45",
          colorInfo: "#183f38",
          colorText: "#182523",
          colorTextSecondary: "#77807d",
          colorBgLayout: "#f6f4ef",
          colorBgContainer: "#ffffff",
          colorBorder: "#ebe5d9",
          borderRadius: 8,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        components: {
          Card: { borderRadiusLG: 8 },
          Button: {
            borderRadius: 8,
            controlHeight: 36,
            primaryShadow: "0 10px 24px rgba(24, 63, 56, 0.18)",
          },
          Layout: { siderBg: "#12332e", bodyBg: "#f6f4ef" },
          Menu: {
            itemBorderRadius: 8,
            itemSelectedBg: "rgba(214, 179, 116, 0.18)",
            itemSelectedColor: "#f5d99c",
            itemColor: "rgba(255,255,255,0.72)",
            itemHoverColor: "#ffffff",
            itemHoverBg: "rgba(255,255,255,0.08)",
          },
          Segmented: {
            itemSelectedBg: "#183f38",
            itemSelectedColor: "#fff8e7",
          },
          Table: {
            headerBg: "#faf7ef",
            headerColor: "#334844",
            rowHoverBg: "#fbf8f1",
          },
          Progress: {
            defaultColor: "#c8a467",
            remainingColor: "#ece7dc",
          },
        },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route index element={<HomePage />} />
                <Route path="subjects" element={<SubjectsPage />} />
                <Route path="practice" element={<PracticePage />} />
                <Route path="wrong" element={<WrongBookPage />} />
                <Route path="favorites" element={<FavoritesPage />} />
                <Route path="exams" element={<ExamsPage />} />
                <Route path="statistics" element={<StatisticsPage />} />
              </Route>
            </Route>
            <Route element={<ProtectedRoute adminOnly />}>
              <Route element={<AppShell />}>
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