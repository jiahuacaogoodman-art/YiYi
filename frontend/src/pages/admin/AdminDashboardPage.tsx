import { Col, Empty, Row, Space, Table, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { BookOpen, ClipboardCheck, FileWarning, Users } from "lucide-react";
import { statisticsApi } from "../../api/client";
import { EChart } from "../../components/EChart";
import { MetricCard } from "../../components/MetricCard";
import type { DashboardStatistics } from "../../types/domain";
import { barOption, lineOption, pieOption } from "../../utils/charts";
import { compactNumber, shortDate, statusLabel } from "../../utils/format";

export function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null);

  useEffect(() => {
    statisticsApi.dashboard().then(setStats);
  }, []);

  const distribution = useMemo(() => {
    const rows = stats?.subject_distribution || [];
    return pieOption(
      "各科题量分布",
      rows.map((row) => ({ name: String(row.subject_name || "-"), value: Number(row.question_count || 0) })),
    );
  }, [stats]);

  const trend = useMemo(() => {
    const rows = stats?.user_practice_trend || [];
    return lineOption(
      "用户刷题趋势",
      rows.map((row) => String(row.date || "")),
      rows.map((row) => Number(row.count || 0)),
    );
  }, [stats]);

  const wrong = useMemo(() => {
    const rows = stats?.top_wrong_knowledge_points || [];
    return barOption(
      "错误率最高知识点",
      rows.map((row) => String(row.knowledge_point_name || "")),
      rows.map((row) => Number(row.wrong_rate || 0)),
    );
  }, [stats]);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>后台控制台</Typography.Title>
          <Typography.Text type="secondary">题库、用户、刷题和反馈的运营总览。</Typography.Text>
        </div>
      </div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="总题目数" value={compactNumber(stats?.total_questions)} hint={`${compactNumber(stats?.published_questions)} 已发布`} icon={<BookOpen size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="待审核/草稿" value={`${compactNumber(stats?.pending_review_questions)} / ${compactNumber(stats?.draft_questions)}`} icon={<ClipboardCheck size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="用户总数" value={compactNumber(stats?.total_users)} hint={`今日刷题 ${compactNumber(stats?.today_practice_count)}`} icon={<Users size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="反馈数量" value={compactNumber(stats?.feedback_count)} hint={`今日新增题 ${compactNumber(stats?.today_new_questions)}`} icon={<FileWarning size={18} />} />
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.subject_distribution?.length ? <EChart option={distribution} /> : <Empty description="暂无题量分布" />}</div>
        </Col>
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.user_practice_trend?.length ? <EChart option={trend} /> : <Empty description="暂无刷题趋势" />}</div>
        </Col>
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.top_wrong_knowledge_points?.length ? <EChart option={wrong} /> : <Empty description="暂无错误率数据" />}</div>
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={12}>
          <div className="panel">
            <div className="panel-title">最近导入记录</div>
            <Table
              rowKey={(row) => String(row.id)}
              pagination={false}
              dataSource={stats?.recent_import_records || []}
              columns={[
                { title: "文件", dataIndex: "file_name" },
                { title: "状态", dataIndex: "status", render: (value) => <Tag>{statusLabel[String(value)] || String(value)}</Tag> },
                { title: "成功/失败", render: (_, row) => `${row.success_count || 0} / ${row.failed_count || 0}` },
                { title: "时间", dataIndex: "created_at", render: (value) => shortDate(String(value)) },
              ]}
            />
          </div>
        </Col>
        <Col xs={24} xl={12}>
          <div className="panel">
            <div className="panel-title">最近管理员操作</div>
            <Space direction="vertical" className="full-width">
              {(stats?.recent_operation_logs || []).length ? (
                stats?.recent_operation_logs.map((row) => (
                  <div className="list-row" key={String(row.id)}>
                    <span>{String(row.summary || row.action || "-")}</span>
                    <Tag>{shortDate(String(row.created_at || ""))}</Tag>
                  </div>
                ))
              ) : (
                <Empty description="暂无操作日志" />
              )}
            </Space>
          </div>
        </Col>
      </Row>
    </div>
  );
}