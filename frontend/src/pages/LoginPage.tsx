import { Button, Card, Form, Input, Segmented, Typography, message } from "antd";
import { useState } from "react";
import { Lock, UserRound } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { authApi } from "../api/client";
import { BrandMark } from "../components/BrandMark";
import { useAuthStore } from "../stores/authStore";

export function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || "/";

  const submit = async (values: { username: string; password: string; nickname?: string; email?: string }) => {
    setLoading(true);
    try {
      if (mode === "register") {
        await authApi.register(values);
        message.success("注册成功，正在登录");
      }
      const user = await login(values.username, values.password);
      navigate(user.role.name === "student" ? from : "/admin", { replace: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-visual__content">
          <BrandMark size="large" />
          <div className="login-visual__copy">
            <Typography.Title>把医学复习做成一套可靠的训练系统</Typography.Title>
            <Typography.Paragraph>
              围绕科目、章节、知识点、错题和考试记录组织学习路径，学生刷题与题库运营在同一平台内闭环。
            </Typography.Paragraph>
          </div>
          <div className="login-visual__proof">
            <div>
              <strong>题库</strong>
              <span>分层管理</span>
            </div>
            <div>
              <strong>训练</strong>
              <span>错题闭环</span>
            </div>
            <div>
              <strong>考试</strong>
              <span>限时测评</span>
            </div>
          </div>
        </div>
      </section>
      <Card className="login-card" variant="borderless">
        <div className="login-card__head">
          <Typography.Title level={2}>{mode === "login" ? "欢迎回来" : "创建学生账号"}</Typography.Title>
          <Typography.Text type="secondary">进入毅医题库，继续今天的医学训练。</Typography.Text>
        </div>
        <Segmented
          block
          value={mode}
          onChange={(value) => setMode(value as "login" | "register")}
          options={[
            { label: "登录", value: "login" },
            { label: "注册学生账号", value: "register" },
          ]}
        />
        <Form layout="vertical" className="login-form" onFinish={submit} initialValues={{ username: "admin", password: "admin123456" }}>
          <Form.Item label="用户名" name="username" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input prefix={<UserRound size={16} />} placeholder="admin" />
          </Form.Item>
          {mode === "register" ? (
            <>
              <Form.Item label="昵称" name="nickname">
                <Input placeholder="例如：临床一班张同学" />
              </Form.Item>
              <Form.Item label="邮箱" name="email">
                <Input placeholder="可选" />
              </Form.Item>
            </>
          ) : null}
          <Form.Item label="密码" name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<Lock size={16} />} placeholder="admin123456" />
          </Form.Item>
          <Button type="primary" htmlType="submit" size="large" block loading={loading}>
            {mode === "login" ? "进入系统" : "注册并进入"}
          </Button>
        </Form>
      </Card>
    </main>
  );
}