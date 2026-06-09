import { Col, Empty, Row, Table, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { BarChart3, CheckCircle2, ListChecks, XCircle } from "lucide-react";
import { statisticsApi } from "../../api/client";
import { EChart } from "../../components/EChart";
import { MetricCard } from "../../components/MetricCard";
import type { UserStatistics } from "../../types/domain";
import { barOption, lineOption } from "../../utils/charts";
import { compactNumber, percent } from "../../utils/format";

export function StatisticsPage() {
  const [stats, setStats] = useState<UserStatistics | null>(null);

  useEffect(() => {
    statisticsApi.user().then(setStats);
  }, []);

  const trendOption = useMemo(() => {
    const rows = stats?.recent_7_days || [];
    return lineOption(
      "最近 7 天刷题趋势",
      rows.map((row) => String(row.date || "")),
      rows.map((row) => Number(row.total || 0)),
    );
  }, [stats]);

  const masteryOption = useMemo(() => {
    const rows = stats?.chapter_mastery || [];
    return barOption(
      "章节掌握度",
      rows.map((row) => String(row.chapter_name || "")),
      rows.map((row) => Number(row.mastery || 0)),
    );
  }, [stats]);

  return (
    <div className="page">
      <div className="page-heading page-heading--hero">
        <div>
          <span className="page-heading__eyebrow">学习画像</span>
          <Typography.Title level={2}>学习统计</Typography.Title>
          <Typography.Text type="secondary">查看正确率、章节掌握度、高频错误知识点和复习建议。</Typography.Text>
        </div>
        <span className="page-heading__badge"><BarChart3 size={18} /> {percent(stats?.correct_rate)} 正确率</span>
      </div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="总刷题数" value={compactNumber(stats?.total_answers)} icon={<ListChecks size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="正确题数" value={compactNumber(stats?.correct_count)} icon={<CheckCircle2 size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="错误题数" value={compactNumber(stats?.wrong_count)} icon={<XCircle size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="正确率" value={percent(stats?.correct_rate)} icon={<BarChart3 size={18} />} />
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={12}>
          <div className="panel">{stats?.recent_7_days?.length ? <EChart option={trendOption} /> : <Empty description="暂无趋势" />}</div>
        </Col>
        <Col xs={24} xl={12}>
          <div className="panel">{stats?.chapter_mastery?.length ? <EChart option={masteryOption} /> : <Empty description="暂无章节掌握度" />}</div>
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={12}>
          <div className="panel">
            <div className="panel-title">各科目正确率</div>
            <Table
              rowKey={(row) => String(row.subject_id)}
              pagination={false}
              dataSource={stats?.subject_accuracy || []}
              columns={[
                { title: "科目", dataIndex: "subject_name" },
                { title: "刷题数", dataIndex: "total" },
                { title: "正确", dataIndex: "correct" },
                { title: "正确率", dataIndex: "correct_rate", render: (value) => percent(Number(value)) },
              ]}
            />
          </div>
        </Col>
        <Col xs={24} xl={12}>
          <div className="panel">
            <div className="panel-title">推荐复习章节</div>
            <Table
              rowKey={(row) => String(row.chapter_id)}
              pagination={false}
              dataSource={stats?.recommended_chapters || []}
              columns={[
                { title: "章节", dataIndex: "chapter_name" },
                { title: "掌握度", dataIndex: "mastery", render: (value) => percent(Number(value)) },
              ]}
            />
          </div>
        </Col>
      </Row>
      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={12}>
          <div className="panel">
            <div className="panel-title">高频错误知识点</div>
            <Table
              rowKey={(row) => String(row.knowledge_point_id)}
              pagination={false}
              dataSource={stats?.high_frequency_wrong_points || []}
              columns={[
                { title: "知识点", dataIndex: "knowledge_point_name" },
                { title: "错误次数", dataIndex: "wrong_count" },
              ]}
            />
          </div>
        </Col>
      </Row>
    </div>
  );
}