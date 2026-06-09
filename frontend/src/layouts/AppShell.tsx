import { Avatar, Button, Dropdown, Layout, Menu, Typography } from "antd";
import type { MenuProps } from "antd";
import {
  BarChart3,
  BookOpen,
  ClipboardList,
  FileSpreadsheet,
  GraduationCap,
  Heart,
  History,
  Home,
  LogOut,
  MessageSquareWarning,
  NotebookTabs,
  Settings,
  ShieldCheck,
  Stethoscope,
  Users,
} from "lucide-react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";

const { Sider, Content } = Layout;

const studentItems: MenuProps["items"] = [
  { key: "/", icon: <Home size={18} />, label: <Link to="/">学习首页</Link> },
  { key: "/subjects", icon: <BookOpen size={18} />, label: <Link to="/subjects">题库选择</Link> },
  { key: "/practice", icon: <NotebookTabs size={18} />, label: <Link to="/practice">开始刷题</Link> },
  { key: "/wrong", icon: <History size={18} />, label: <Link to="/wrong">错题本</Link> },
  { key: "/favorites", icon: <Heart size={18} />, label: <Link to="/favorites">收藏题</Link> },
  { key: "/exams", icon: <ClipboardList size={18} />, label: <Link to="/exams">模拟考试</Link> },
  { key: "/statistics", icon: <BarChart3 size={18} />, label: <Link to="/statistics">学习统计</Link> },
];

const adminItems: MenuProps["items"] = [
  { key: "/admin", icon: <ShieldCheck size={18} />, label: <Link to="/admin">后台控制台</Link> },
  { key: "/admin/subjects", icon: <BookOpen size={18} />, label: <Link to="/admin/subjects">科目分栏</Link> },
  { key: "/admin/chapters", icon: <BookOpen size={18} />, label: <Link to="/admin/chapters">章节管理</Link> },
  { key: "/admin/knowledge-points", icon: <BookOpen size={18} />, label: <Link to="/admin/knowledge-points">知识点管理</Link> },
  { key: "/admin/questions", icon: <NotebookTabs size={18} />, label: <Link to="/admin/questions">题目管理</Link> },
  { key: "/admin/import", icon: <FileSpreadsheet size={18} />, label: <Link to="/admin/import">批量导入题目</Link> },
  { key: "/admin/exams", icon: <ClipboardList size={18} />, label: <Link to="/admin/exams">套卷管理</Link> },
  { key: "/admin/users", icon: <Users size={18} />, label: <Link to="/admin/users">用户管理</Link> },
  { key: "/admin/feedback", icon: <MessageSquareWarning size={18} />, label: <Link to="/admin/feedback">反馈纠错</Link> },
  { key: "/admin/statistics", icon: <BarChart3 size={18} />, label: <Link to="/admin/statistics">数据统计</Link> },
  { key: "/admin/logs", icon: <History size={18} />, label: <Link to="/admin/logs">操作日志</Link> },
  { key: "/admin/settings", icon: <Settings size={18} />, label: <Link to="/admin/settings">系统设置</Link> },
];

function selectedKey(pathname: string) {
  const all = [...(studentItems || []), ...(adminItems || [])].map((item) => String(item?.key || ""));
  return all
    .filter((key) => key === "/" ? pathname === "/" : pathname.startsWith(key))
    .sort((a, b) => b.length - a.length)[0] || "/";
}

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const isAdmin = user?.role.name !== "student";

  const accountItems: MenuProps["items"] = [
    { key: "student", label: "学生端", onClick: () => navigate("/") },
    ...(isAdmin ? [{ key: "admin", label: "管理后台", onClick: () => navigate("/admin") }] : []),
    { type: "divider" },
    {
      key: "logout",
      danger: true,
      icon: <LogOut size={16} />,
      label: "退出登录",
      onClick: async () => {
        await logout();
        navigate("/login");
      },
    },
  ];

  return (
    <Layout className="app-shell">
      <Sider className="app-sider" width={252} breakpoint="lg" collapsedWidth={0}>
        <Link to="/" className="brand">
          <span className="brand__mark">
            <Stethoscope size={22} />
          </span>
          <span>
            <strong>医学刷题平台</strong>
            <small>题库与考试系统</small>
          </span>
        </Link>
        <div className="menu-section">学生端</div>
        <Menu mode="inline" selectedKeys={[selectedKey(location.pathname)]} items={studentItems} />
        {isAdmin ? (
          <>
            <div className="menu-section">管理后台</div>
            <Menu mode="inline" selectedKeys={[selectedKey(location.pathname)]} items={adminItems} />
          </>
        ) : null}
      </Sider>
      <Layout>
        <header className="topbar">
          <div>
            <Typography.Text type="secondary">中文医学题库运营系统</Typography.Text>
          </div>
          <Dropdown menu={{ items: accountItems }} placement="bottomRight">
            <Button type="text" className="account-button">
              <Avatar size={30} icon={<GraduationCap size={16} />} />
              <span>{user?.nickname || user?.username}</span>
            </Button>
          </Dropdown>
        </header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}