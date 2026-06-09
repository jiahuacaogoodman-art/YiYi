import { Avatar, Button, Dropdown, Layout, Menu, Typography } from "antd";
import type { MenuProps } from "antd";
import {
  BarChart3,
  BookOpen,
  ClipboardList,
  FileSpreadsheet,
  GraduationCap,
  History,
  Home,
  LogOut,
  MessageSquareWarning,
  NotebookTabs,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { BrandMark } from "../components/BrandMark";
import { useAuthStore } from "../stores/authStore";

const { Sider, Content } = Layout;

const adminItems: Required<MenuProps>["items"] = [
  { key: "/admin", icon: <ShieldCheck size={18} />, label: <Link to="/admin">控制台</Link> },
  { key: "/admin/questions", icon: <NotebookTabs size={18} />, label: <Link to="/admin/questions">题目管理</Link> },
  { key: "/admin/import", icon: <FileSpreadsheet size={18} />, label: <Link to="/admin/import">批量导入</Link> },
  { key: "/admin/subjects", icon: <BookOpen size={18} />, label: <Link to="/admin/subjects">科目结构</Link> },
  { key: "/admin/chapters", icon: <BookOpen size={18} />, label: <Link to="/admin/chapters">章节管理</Link> },
  { key: "/admin/knowledge-points", icon: <BookOpen size={18} />, label: <Link to="/admin/knowledge-points">知识点管理</Link> },
  { key: "/admin/exams", icon: <ClipboardList size={18} />, label: <Link to="/admin/exams">套卷管理</Link> },
  { key: "/admin/users", icon: <Users size={18} />, label: <Link to="/admin/users">用户管理</Link> },
  { key: "/admin/feedback", icon: <MessageSquareWarning size={18} />, label: <Link to="/admin/feedback">反馈纠错</Link> },
  { key: "/admin/statistics", icon: <BarChart3 size={18} />, label: <Link to="/admin/statistics">数据统计</Link> },
  { key: "/admin/logs", icon: <History size={18} />, label: <Link to="/admin/logs">操作日志</Link> },
  { key: "/admin/settings", icon: <Settings size={18} />, label: <Link to="/admin/settings">系统设置</Link> },
];

function selectedKey(pathname: string) {
  return adminItems
    .map((item) => String(item?.key || ""))
    .filter((key) => pathname === key || pathname.startsWith(`${key}/`))
    .sort((a, b) => b.length - a.length)[0] || "/admin";
}

export function AdminShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const accountItems: MenuProps["items"] = [
    { key: "student", icon: <Home size={16} />, label: "返回学生端", onClick: () => navigate("/") },
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
    <Layout className="admin-shell">
      <Sider className="admin-sider" width={264} breakpoint="lg" collapsedWidth={0}>
        <Link to="/admin" className="admin-brand">
          <BrandMark size="small" />
          <span>管理后台</span>
        </Link>
        <div className="admin-menu-section">运营管理</div>
        <Menu mode="inline" selectedKeys={[selectedKey(location.pathname)]} items={adminItems} />
      </Sider>
      <Layout className="admin-main">
        <header className="admin-topbar">
          <div className="admin-topbar__title">
            <Typography.Text type="secondary">YiYi Admin Console</Typography.Text>
            <strong>题库运营中心</strong>
          </div>
          <Dropdown menu={{ items: accountItems }} placement="bottomRight">
            <Button type="text" className="admin-account">
              <Avatar size={30} icon={<GraduationCap size={16} />} />
              <span>{user?.nickname || user?.username}</span>
            </Button>
          </Dropdown>
        </header>
        <Content className="admin-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}