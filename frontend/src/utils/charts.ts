import type { EChartsOption } from "echarts";

export function lineOption(title: string, labels: string[], values: number[]): EChartsOption {
  return {
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 600 }, left: 0 },
    tooltip: { trigger: "axis" },
    grid: { left: 32, right: 16, top: 44, bottom: 28 },
    xAxis: { type: "category", data: labels, axisTick: { show: false } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#edf1f7" } } },
    series: [{ type: "line", smooth: true, data: values, areaStyle: { opacity: 0.12 }, lineStyle: { width: 3 } }],
  };
}

export function barOption(title: string, labels: string[], values: number[]): EChartsOption {
  return {
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 600 }, left: 0 },
    tooltip: { trigger: "axis" },
    grid: { left: 36, right: 16, top: 44, bottom: 36 },
    xAxis: { type: "category", data: labels, axisLabel: { interval: 0, rotate: labels.length > 6 ? 24 : 0 } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#edf1f7" } } },
    series: [{ type: "bar", data: values, barMaxWidth: 34, itemStyle: { borderRadius: [4, 4, 0, 0] } }],
  };
}

export function pieOption(title: string, data: Array<{ name: string; value: number }>): EChartsOption {
  return {
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 600 }, left: 0 },
    tooltip: { trigger: "item" },
    legend: { bottom: 0, type: "scroll" },
    series: [{ type: "pie", radius: ["42%", "68%"], center: ["50%", "45%"], data }],
  };
}