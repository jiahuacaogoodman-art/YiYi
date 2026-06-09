import { Avatar, Button, Dropdown, Layout, Menu, Typography } from "antd";
import type { MenuProps } from "antd";
import {
  BarChart3,
  BookOpen,
  ClipboardList,
  GraduationCap,
  Heart,
  History,
  Home,
  LogOut,
  MessageSquare,
  NotebookPen,
  NotebookTabs,
  ThumbsUp,
} from "lucide-react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { BrandMark } from "../components/BrandMark";
import { useAuthStore } from "../stores/authStore";

const { Sider, Content } = Layout;

const studentItems: Required<MenuProps>["items"] = [
  { key: "/", icon: <Home size={18} />, label: <Link to="/">学习首页</Link> },
  { key: "/subjects", icon: <BookOpen size={18} />, label: <Link to="/subjects">题库选择</Link> },
  { key: "/practice", icon: <NotebookTabs size={18} />, label: <Link to="/practice">开始刷题</Link> },
  { key: "/wrong", icon: <History size={18} />, label: <Link to="/wrong">错题本</Link> },
  { key: "/favorites", icon: <Heart size={18} />, label: <Link to="/favorites">收藏题</Link> },
  { key: "/notes", icon: <NotebookPen size={18} />, label: <Link to="/notes">我的笔记</Link> },
  { key: "/comments", icon: <MessageSquare size={18} />, label: <Link to="/comments">我的评论</Link> },
  { key: "/likes", icon: <ThumbsUp size={18} />, label: <Link to="/likes">我的点赞</Link> },
  { key: "/exams", icon: <ClipboardList size={18} />, label: <Link to="/exams">模拟考试</Link> },
  { key: "/statistics", icon: <BarChart3 size={18} />, label: <Link to="/statistics">学习统计</Link> },
];

const mobileItems = [
  { key: "/", icon: <Home size={20} />, label: "首页" },
  { key: "/subjects", icon: <BookOpen size={20} />, label: "题库" },
  { key: "/practice", icon: <NotebookTabs size={20} />, label: "刷题" },
  { key: "/notes", icon: <NotebookPen size={20} />, label: "笔记" },
  { key: "/statistics", icon: <BarChart3 size={20} />, label: "我的" },
];

function selectedKey(pathname: string) {
  return studentItems
    .map((item) => String(item?.key || ""))
    .filter((key) => (key === "/" ? pathname === "/" : pathname.startsWith(key)))
    .sort((a, b) => b.length - a.length)[0] || "/";
}

export function StudentShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const isAdmin = user?.role.name !== "student";

  const accountItems: MenuProps["items"] = [
    ...(isAdmin ? [{ key: "admin", label: "进入管理后台", onClick: () => navigate("/admin") }] : []),
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
    <Layout className="app-shell student-shell">
      <Sider className="app-sider student-sider" width={252} breakpoint="lg" collapsedWidth={0}>
        <Link to="/" className="brand">
          <BrandMark />
        </Link>
        <div className="menu-section">学习端</div>
        <Menu mode="inline" selectedKeys={[selectedKey(location.pathname)]} items={studentItems} />
      </Sider>
      <Layout>
        <header className="topbar student-topbar">
          <div className="topbar__title">
            <Typography.Text type="secondary">医学教育 · 智能题库平台</Typography.Text>
            <strong>学习工作台</strong>
          </div>
          <Dropdown menu={{ items: accountItems }} placement="bottomRight">
            <Button type="text" className="account-button">
              <Avatar size={30} icon={<GraduationCap size={16} />} />
              <span>{user?.nickname || user?.username}</span>
            </Button>
          </Dropdown>
        </header>
        <Content className="app-content student-content">
          <Outlet />
        </Content>
        <nav className="mobile-tabbar" aria-label="学生端快捷导航">
          {mobileItems.map((item) => (
            <Link
              key={item.key}
              className={selectedKey(location.pathname) === item.key ? "mobile-tabbar__item mobile-tabbar__item--active" : "mobile-tabbar__item"}
              to={item.key}
            >
              <span className="mobile-tabbar__icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </Layout>
    </Layout>
  );
}