import React, { useState, useEffect, useRef } from 'react';
import { Download, RefreshCw, TrendingUp, MessageSquare, ShoppingCart, Heart, Calendar, Users, Activity, BarChart3, PieChart, FileText } from 'lucide-react';
import * as echarts from 'echarts';
import { getAnalyticsReport, exportAnalyticsReport } from '../api/api';

function AnalyticsPage({ onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('today'); // today, week, month

  const sessionsChartRef = useRef(null);
  const intentChartRef = useRef(null);
  const productsChartRef = useRef(null);
  const trendChartRef = useRef(null);
  const behaviorChartRef = useRef(null);

  const sessionsChartInstanceRef = useRef(null);
  const intentChartInstanceRef = useRef(null);
  const productsChartInstanceRef = useRef(null);
  const trendChartInstanceRef = useRef(null);
  const behaviorChartInstanceRef = useRef(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const report = await getAnalyticsReport(1);
      console.log('加载分析数据成功:', report);
      setData(report);
    } catch (err) {
      console.error('加载分析数据失败:', err);
      setError('加载失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      await exportAnalyticsReport(1);
      alert('报告导出成功！');
    } catch (err) {
      console.error('导出失败:', err);
      alert('导出失败，请重试');
    }
  };

  // 初始化会话统计图表
  useEffect(() => {
    console.log('初始化会话统计图表');
    // 使用 setTimeout 确保 DOM 已经渲染，增加延迟到 300ms
    const timer = setTimeout(() => {
      console.log('setTimeout 执行，检查 sessionsChartRef.current');
      if (!sessionsChartRef.current) {
        console.warn('sessionsChartRef.current 为空，DOM 可能未就绪');
        return;
      }
      console.log('sessionsChartRef.current 存在，开始初始化图表');

      try {
        const chart = echarts.init(sessionsChartRef.current);
        sessionsChartInstanceRef.current = chart;
        console.log('会话统计图表初始化成功，实例已创建');

        // 如果数据已经存在，立即设置
        if (data) {
          console.log('数据已存在，立即设置图表选项');

          // 计算移动平均（简单趋势预测）
          const sessionData = [
            data.session_stats.total_sessions || 0,
            data.session_stats.today_sessions || 0,
            data.session_stats.total_messages || 0,
            data.session_stats.avg_messages_per_session || 0
          ];

          const calculateTrend = (dataArray) => {
            const result = [];
            for (let i = 0; i < dataArray.length; i++) {
              // 简单的2点移动平均
              if (i === 0) {
                result.push(dataArray[i]);
              } else {
                result.push((dataArray[i - 1] + dataArray[i]) / 2);
              }
            }
            return result;
          };

          const trendData = calculateTrend(sessionData);

          const sessionsOption = {
            title: {
              text: '会话统计概览',
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' }
            },
            tooltip: {
              trigger: 'axis',
              formatter: (params) => {
                let result = params[0].name + '<br/>';
                params.forEach(param => {
                  const seriesName = param.seriesName;
                  const value = typeof param.value === 'number' ? param.value.toFixed(2) : param.value;
                  result += `${seriesName}: ${value}<br/>`;
                });
                return result;
              },
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              textStyle: { color: '#1f2937' }
            },
            grid: {
              left: '3%',
              right: '4%',
              bottom: '3%',
              containLabel: true
            },
            xAxis: {
              type: 'category',
              data: ['总会话数', '今日会话', '总消息数', '平均消息/会话'],
              axisLabel: {
                interval: 0,
                rotate: 0,
                color: '#6b7280',
                fontSize: 12
              },
              axisLine: { lineStyle: { color: '#e5e7eb' } }
            },
            yAxis: {
              type: 'value',
              name: '数量',
              nameTextStyle: { color: '#6b7280' },
              axisLabel: { color: '#6b7280' },
              splitLine: { lineStyle: { color: '#f3f4f6' } }
            },
            series: [
              {
                name: '数量',
                type: 'bar',
                data: sessionData,
                itemStyle: {
                  borderRadius: [8, 8, 0, 0],
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#667eea' },
                    { offset: 1, color: '#764ba2' }
                  ])
                },
                barWidth: '50%',
                showBackground: true,
                backgroundStyle: {
                  color: 'rgba(0, 0, 0, 0.05)',
                  borderRadius: [8, 8, 0, 0]
                }
              },
              {
                name: '趋势线',
                type: 'line',
                data: trendData,
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: {
                  width: 3,
                  color: '#f59e0b'
                },
                itemStyle: {
                  color: '#f59e0b',
                  borderColor: '#fff',
                  borderWidth: 2
                },
                markLine: {
                  symbol: 'none',
                  label: {
                    show: true,
                    position: 'end',
                    formatter: '平均值: {c}',
                    fontSize: 11
                  },
                  lineStyle: {
                    color: '#10b981',
                    type: 'dashed',
                    width: 2
                  },
                  data: [
                    {
                      type: 'average',
                      name: '平均值'
                    }
                  ]
                }
              }
            ]
          };
          chart.setOption(sessionsOption);
          console.log('会话统计图表设置完成');

          // 使用 requestAnimationFrame 确保 DOM 完全渲染后再调整大小
          requestAnimationFrame(() => {
            chart.resize();
            console.log('会话统计图表 resize 完成');
          });
        }

        const handleResize = () => {
          if (sessionsChartInstanceRef.current) {
            sessionsChartInstanceRef.current.resize();
          }
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          if (sessionsChartInstanceRef.current) {
            sessionsChartInstanceRef.current.dispose();
            sessionsChartInstanceRef.current = null;
          }
        };
      } catch (error) {
        console.error('会话统计图表初始化失败:', error);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  // 初始化意图分布图表
  useEffect(() => {
    console.log('初始化意图分布图表');
    const timer = setTimeout(() => {
      console.log('setTimeout 执行，检查 intentChartRef.current');
      if (!intentChartRef.current) {
        console.warn('intentChartRef.current 为空，DOM 可能未就绪');
        return;
      }
      console.log('intentChartRef.current 存在，开始初始化图表');

      try {
        const chart = echarts.init(intentChartRef.current);
        intentChartInstanceRef.current = chart;
        console.log('意图分布图表初始化成功，实例已创建');

        // 如果数据已经存在，立即设置
        if (data) {
          console.log('数据已存在，立即设置意图分布图表选项');
          const intentOption = {
            title: {
              text: '用户意图分布',
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' }
            },
            tooltip: {
              trigger: 'item',
              formatter: '{b}<br/>数量: {c}<br/>占比: {d}%',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              textStyle: { color: '#1f2937' }
            },
            legend: {
              orient: 'vertical',
              left: '5%',
              top: 'middle',
              textStyle: { color: '#6b7280', fontSize: 12 }
            },
            series: [
              {
                name: '意图分布',
                type: 'pie',
                radius: ['35%', '65%'],
                avoidLabelOverlap: true,
                itemStyle: {
                  borderRadius: 8,
                  borderColor: '#fff',
                  borderWidth: 3
                },
                label: {
                  show: true,
                  formatter: '{b}\n{d}%',
                  color: '#374151',
                  fontSize: 11
                },
                emphasis: {
                  label: {
                    show: true,
                    fontSize: 14,
                    fontWeight: 'bold'
                  },
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                },
                data: data.intent_distribution && data.intent_distribution.length > 0
                  ? data.intent_distribution.map((item, index) => ({
                      name: item.intent,
                      value: item.count,
                      itemStyle: {
                        color: [
                          '#667eea',
                          '#764ba2',
                          '#f093fb',
                          '#f5576c',
                          '#4facfe',
                          '#00f2fe'
                        ][index % 6]
                      }
                    }))
                  : [{ name: '暂无数据', value: 0, itemStyle: { color: '#e5e7eb' } }]
              }
            ]
          };
          chart.setOption(intentOption);
          console.log('意图分布图表设置完成');

          // 使用 requestAnimationFrame 确保 DOM 完全渲染后再调整大小
          requestAnimationFrame(() => {
            chart.resize();
            console.log('意图分布图表 resize 完成');
          });
        }

        const handleResize = () => {
          if (intentChartInstanceRef.current) {
            intentChartInstanceRef.current.resize();
          }
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          if (intentChartInstanceRef.current) {
            intentChartInstanceRef.current.dispose();
            intentChartInstanceRef.current = null;
          }
        };
      } catch (error) {
        console.error('意图分布图表初始化失败:', error);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  // 初始化热门商品图表
  useEffect(() => {
    console.log('初始化热门商品图表');
    const timer = setTimeout(() => {
      console.log('setTimeout 执行，检查 productsChartRef.current');
      if (!productsChartRef.current) {
        console.warn('productsChartRef.current 为空，DOM 可能未就绪');
        return;
      }
      console.log('productsChartRef.current 存在，开始初始化图表');

      try {
        const chart = echarts.init(productsChartRef.current);
        productsChartInstanceRef.current = chart;
        console.log('热门商品图表初始化成功，实例已创建');

        // 如果数据已经存在，立即设置
        if (data) {
          console.log('数据已存在，立即设置热门商品图表选项');

          const topProducts = data.top_products && data.top_products.length > 0
            ? data.top_products.slice(0, 10)
            : [];

          const productData = topProducts.map(p => ({
            value: p.recommendation_count,
            itemStyle: {
              borderRadius: [0, 8, 8, 0],
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#4facfe' },
                { offset: 1, color: '#00f2fe' }
              ])
            }
          }));

          const avgRecommendations = topProducts.length > 0
            ? topProducts.reduce((sum, p) => sum + p.recommendation_count, 0) / topProducts.length
            : 0;

          const productsOption = {
            title: {
              text: '热门商品排行 TOP 10',
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' }
            },
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'shadow'
              },
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              textStyle: { color: '#1f2937' },
              formatter: '{b}<br/>推荐次数: {c}'
            },
            grid: {
              left: '3%',
              right: '8%',
              bottom: '3%',
              top: '15%',
              containLabel: true
            },
            xAxis: {
              type: 'value',
              name: '推荐次数',
              nameTextStyle: { color: '#6b7280' },
              axisLabel: { color: '#6b7280' },
              splitLine: { lineStyle: { color: '#f3f4f6' } }
            },
            yAxis: {
              type: 'category',
              data: topProducts.length > 0
                ? topProducts.map(p => p.name)
                : ['暂无数据'],
              axisLabel: {
                interval: 0,
                width: 180,
                overflow: 'truncate',
                ellipsis: '...',
                color: '#6b7280',
                fontSize: 12
              },
              axisLine: { lineStyle: { color: '#e5e7eb' } }
            },
            series: [
              {
                name: '热度',
                type: 'bar',
                data: topProducts.length > 0 ? productData : [0],
                barWidth: '60%',
                showBackground: true,
                backgroundStyle: {
                  color: 'rgba(0, 0, 0, 0.03)',
                  borderRadius: [0, 8, 8, 0]
                },
                label: {
                  show: true,
                  position: 'right',
                  color: '#374151',
                  fontSize: 12,
                  fontWeight: 'bold'
                },
                markLine: {
                  symbol: 'none',
                  label: {
                    show: true,
                    position: 'end',
                    formatter: '平均值: {c}',
                    fontSize: 11
                  },
                  lineStyle: {
                    color: '#10b981',
                    type: 'dashed',
                    width: 2
                  },
                  data: [
                    {
                      xAxis: avgRecommendations,
                      name: '平均值',
                      label: {
                        formatter: `平均值: ${avgRecommendations.toFixed(1)}`
                      }
                    }
                  ]
                }
              }
            ]
          };
          chart.setOption(productsOption);
          console.log('热门商品图表设置完成');

          // 使用 requestAnimationFrame 确保 DOM 完全渲染后再调整大小
          requestAnimationFrame(() => {
            chart.resize();
            console.log('热门商品图表 resize 完成');
          });
        }

        const handleResize = () => {
          if (productsChartInstanceRef.current) {
            productsChartInstanceRef.current.resize();
          }
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          if (productsChartInstanceRef.current) {
            productsChartInstanceRef.current.dispose();
            productsChartInstanceRef.current = null;
          }
        };
      } catch (error) {
        console.error('热门商品图表初始化失败:', error);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  // 初始化用户行为图表
  useEffect(() => {
    console.log('初始化用户行为图表');
    const timer = setTimeout(() => {
      console.log('setTimeout 执行，检查 behaviorChartRef.current');
      if (!behaviorChartRef.current) {
        console.warn('behaviorChartRef.current 为空，DOM 可能未就绪');
        return;
      }
      console.log('behaviorChartRef.current 存在，开始初始化图表');

      try {
        const chart = echarts.init(behaviorChartRef.current);
        behaviorChartInstanceRef.current = chart;
        console.log('用户行为图表初始化成功，实例已创建');

        // 如果数据已经存在，立即设置
        if (data) {
          console.log('数据已存在，立即设置用户行为图表选项');
          const behaviorOption = {
            title: {
              text: '用户行为统计',
              left: 'center',
              textStyle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937' }
            },
            tooltip: {
              trigger: 'item',
              formatter: '{b}<br/>数量: {c}<br/>占比: {d}%',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderColor: '#e5e7eb',
              borderWidth: 1,
              textStyle: { color: '#1f2937' }
            },
            legend: {
              orient: 'horizontal',
              bottom: '5%',
              textStyle: { color: '#6b7280', fontSize: 12 }
            },
            series: [
              {
                name: '用户行为',
                type: 'pie',
                radius: ['40%', '65%'],
                avoidLabelOverlap: true,
                itemStyle: {
                  borderRadius: 8,
                  borderColor: '#fff',
                  borderWidth: 3
                },
                label: {
                  show: true,
                  formatter: '{b}\n{d}%',
                  color: '#374151',
                  fontSize: 11
                },
                emphasis: {
                  label: {
                    show: true,
                    fontSize: 14,
                    fontWeight: 'bold'
                  },
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                },
                data: [
                  {
                    name: '购物车操作',
                    value: data.user_behavior.total_cart_operations || 0,
                    itemStyle: { color: '#f5576c' }
                  },
                  {
                    name: '收藏操作',
                    value: data.user_behavior.total_wishlist_operations || 0,
                    itemStyle: { color: '#f093fb' }
                  },
                  {
                    name: '商品浏览',
                    value: data.user_behavior.total_product_views || 0,
                    itemStyle: { color: '#4facfe' }
                  },
                  {
                    name: '反馈提交',
                    value: data.user_behavior.total_feedbacks || 0,
                    itemStyle: { color: '#00f2fe' }
                  }
                ].filter(item => item.value > 0)
              }
            ]
          };
          chart.setOption(behaviorOption);
          console.log('用户行为图表设置完成');

          // 使用 requestAnimationFrame 确保 DOM 完全渲染后再调整大小
          requestAnimationFrame(() => {
            chart.resize();
            console.log('用户行为图表 resize 完成');
          });
        }

        const handleResize = () => {
          if (behaviorChartInstanceRef.current) {
            behaviorChartInstanceRef.current.resize();
          }
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          if (behaviorChartInstanceRef.current) {
            behaviorChartInstanceRef.current.dispose();
            behaviorChartInstanceRef.current = null;
          }
        };
      } catch (error) {
        console.error('用户行为图表初始化失败:', error);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  // 加载初始数据
  useEffect(() => {
    console.log('=== AnalyticsPage 组件挂载 ===');
    console.log('当前 timeRange:', timeRange);
    console.log('窗口宽度:', window.innerWidth, '断点:', window.innerWidth < 640 ? 'sm' : window.innerWidth < 768 ? 'md' : window.innerWidth < 1024 ? 'lg' : 'xl');
    loadData();
  }, [timeRange]);

  // 监控窗口大小变化并动态更新grid布局
  useEffect(() => {
    const updateGridLayout = () => {
      const width = window.innerWidth;
      const gridElements = document.querySelectorAll('[data-grid-responsive="true"]');
      gridElements.forEach(el => {
        let cols = 2; // 默认 2 列
        if (width >= 1024) {
          cols = 4; // lg
        } else if (width >= 768) {
          cols = 3; // md
        } else if (width >= 640) {
          cols = 2; // sm
        }
        el.style.display = 'grid';
        el.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
        el.style.gap = '1rem';
        console.log(`更新 grid: 宽度=${width}, 列数=${cols}`);
      });
    };

    updateGridLayout();

    const handleResize = () => {
      console.log('窗口大小变化:', window.innerWidth, 'x', window.innerHeight);
      updateGridLayout();
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 调试：数据加载完成后打印
  useEffect(() => {
    if (data) {
      console.log('=== 数据加载完成 ===');
      console.log('会话统计:', data.session_stats);
      console.log('用户行为:', data.user_behavior);
      console.log('热门商品:', data.top_products);
      console.log('意图分布:', data.intent_distribution);
      console.log('图表实例状态:', {
        sessions: !!sessionsChartInstanceRef.current,
        intent: !!intentChartInstanceRef.current,
        products: !!productsChartInstanceRef.current,
        behavior: !!behaviorChartInstanceRef.current
      });
      console.log('图表 ref 状态:', {
        sessions: !!sessionsChartRef.current,
        intent: !!intentChartRef.current,
        products: !!productsChartRef.current,
        behavior: !!behaviorChartRef.current
      });
    }
  }, [data]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600"></div>
          <p className="mt-6 text-lg text-gray-700 font-medium">加载分析数据中...</p>
          <p className="mt-2 text-sm text-gray-500">请稍候，正在获取最新数据</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-red-50 to-orange-50">
        <div className="text-center bg-white p-8 rounded-2xl shadow-xl max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <p className="text-red-600 mb-6 text-lg font-medium">{error}</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={loadData}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-200"
            >
              <RefreshCw className="w-4 h-4" />
              重试
            </button>
            <button
              onClick={onBack}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors"
            >
              返回
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="analytics-page min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* 顶部操作栏 - 移除minWidth限制 */}
      <div className="bg-white shadow-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 rounded-xl hover:shadow-md transition-all duration-200 font-medium"
              >
                ← 返回
              </button>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                📊 数据分析报告
              </h1>
            </div>
            <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-gray-700 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 cursor-pointer"
              >
                <option value="today">今日</option>
                <option value="week">本周</option>
                <option value="month">本月</option>
              </select>
              <button
                onClick={loadData}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 text-sm font-medium"
              >
                <RefreshCw className="w-4 h-4" />
                刷新
              </button>
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 text-sm font-medium"
              >
                <Download className="w-4 h-4" />
                导出报告
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="w-full px-6 py-8 sm:px-8 sm:py-10 max-w-7xl mx-auto">
        {/* 统计卡片 - 美化布局 */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5 md:gap-6 mb-8 sm:mb-10"
             style={{
               display: 'grid',
               gridTemplateColumns: 'repeat(3, 1fr)',
               gap: '1.5rem',
               marginBottom: '2.5rem'
             }}
             data-grid-responsive="true">
          <StatCard
            icon={<Activity className="w-6 h-6 sm:w-7 sm:h-7 text-blue-600" />}
            title="总会话数"
            value={data.session_stats.total_sessions || 0}
            color="blue"
            trend="+12%"
            trendUp={true}
          />
          <StatCard
            icon={<MessageSquare className="w-6 h-6 sm:w-7 sm:h-7 text-green-600" />}
            title="今日会话"
            value={data.session_stats.today_sessions || 0}
            color="green"
            trend="+5%"
            trendUp={true}
          />
          <StatCard
            icon={<ShoppingCart className="w-6 h-6 sm:w-7 sm:h-7 text-purple-600" />}
            title="购物车操作"
            value={data.user_behavior.total_cart_operations || 0}
            color="purple"
            trend="+8%"
            trendUp={true}
          />
          <StatCard
            icon={<Heart className="w-6 h-6 sm:w-7 sm:h-7 text-red-600" />}
            title="收藏操作"
            value={data.user_behavior.total_wishlist_operations || 0}
            color="red"
            trend="+15%"
            trendUp={true}
          />
        </div>

        {/* 快速统计 - 美化布局 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-5 md:gap-6 mb-8 sm:mb-10"
             style={{
               display: 'grid',
               gridTemplateColumns: 'repeat(3, 1fr)',
               gap: '1.5rem',
               marginBottom: '2.5rem'
             }}
             data-grid-responsive="true">
          <QuickStat
            icon={<Users className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600" />}
            title="总用户数"
            value={data.session_stats.total_users || 0}
            color="indigo"
          />
          <QuickStat
            icon={<FileText className="w-5 h-5 sm:w-6 sm:h-6 text-amber-600" />}
            title="总消息数"
            value={data.session_stats.total_messages || 0}
            color="amber"
          />
          <QuickStat
            icon={<BarChart3 className="w-5 h-5 sm:w-6 sm:h-6 text-cyan-600" />}
            title="平均消息/会话"
            value={data.session_stats.avg_messages_per_session?.toFixed(2) || '0.00'}
            color="cyan"
          />
        </div>

        {/* 图表区域 - 美化布局 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 mb-8 sm:mb-10"
             style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem', marginBottom: '2.5rem' }}>
          {/* 会话统计图表 */}
          <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-800">会话统计概览</h3>
            </div>
            <div ref={sessionsChartRef} style={{ width: '100%', height: '320px' }}></div>
          </div>

          {/* 意图分布图表 */}
          <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg">
                <PieChart className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-800">用户意图分布</h3>
            </div>
            <div ref={intentChartRef} style={{ width: '100%', height: '320px' }}></div>
          </div>
        </div>

        {/* 用户行为和热门商品 - 美化布局 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 mb-8 sm:mb-10"
             style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem', marginBottom: '2.5rem' }}>
          {/* 用户行为统计 */}
          <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-gradient-to-br from-pink-500 to-pink-600 rounded-lg">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-800">用户行为统计</h3>
            </div>
            <div ref={behaviorChartRef} style={{ width: '100%', height: '320px' }}></div>
          </div>

          {/* 热门商品排行 */}
          <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-gray-100">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-800">热门商品排行 TOP 10</h3>
            </div>
            <div ref={productsChartRef} style={{ width: '100%', height: '320px' }}></div>
          </div>
        </div>

        {/* 详细数据表格 - 美化布局 */}
        <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 sm:p-8 border border-gray-100">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">详细数据</h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8"
               style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2.5rem' }}>
            {/* 会话详情 */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
              <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-3">
                <div className="p-2 bg-blue-500 rounded-lg">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                会话统计
              </h4>
              <div className="space-y-3">
                <DetailItem label="总会话数" value={data.session_stats.total_sessions || 0} />
                <DetailItem label="今日会话" value={data.session_stats.today_sessions || 0} />
                <DetailItem label="总消息数" value={data.session_stats.total_messages || 0} />
                <DetailItem label="平均消息/会话" value={data.session_stats.avg_messages_per_session?.toFixed(2) || '0.00'} />
                <DetailItem label="总用户数" value={data.session_stats.total_users || 0} />
              </div>
            </div>

            {/* 用户行为 */}
            <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-2xl p-6 border border-pink-200">
              <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-3">
                <div className="p-2 bg-pink-500 rounded-lg">
                  <Users className="w-5 h-5 text-white" />
                </div>
                用户行为
              </h4>
              <div className="space-y-3">
                <DetailItem label="总购物车操作" value={data.user_behavior.total_cart_operations || 0} />
                <DetailItem label="总收藏操作" value={data.user_behavior.total_wishlist_operations || 0} />
                <DetailItem label="商品浏览次数" value={data.user_behavior.total_product_views || 0} />
                <DetailItem label="反馈提交次数" value={data.user_behavior.total_feedbacks || 0} />
              </div>
            </div>
          </div>

          {/* 热门商品列表 - 美化表格 */}
          {data.top_products && data.top_products.length > 0 && (
            <div className="mt-8">
              <h4 className="font-bold text-lg mb-5 text-gray-800 flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                热门商品 TOP {data.top_products.length}
              </h4>
              <div className="overflow-hidden rounded-2xl border border-gray-200 shadow-sm">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">排名</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">商品名称</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">类别</th>
                      <th className="px-6 py-4 text-left text-xs font-bold text-white uppercase tracking-wider">推荐次数</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-100">
                    {data.top_products.map((product, index) => (
                      <tr key={product.product_id} className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg ${
                              index === 0 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' :
                              index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-400' :
                              index === 2 ? 'bg-gradient-to-br from-amber-600 to-amber-700' :
                              'bg-gradient-to-br from-gray-200 to-gray-300'
                            }`}>
                              {index + 1}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          {product.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 rounded-full text-xs font-semibold">
                            {product.category}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full text-sm font-bold shadow-md">
                            {product.recommendation_count}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 意图分布列表 - 美化卡片 */}
          {data.intent_distribution && data.intent_distribution.length > 0 && (
            <div className="mt-8">
              <h4 className="font-bold text-lg mb-5 text-gray-800 flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-violet-500 to-violet-600 rounded-lg">
                  <PieChart className="w-5 h-5 text-white" />
                </div>
                意图分布
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4 sm:gap-5"
                   style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem' }}>
                {data.intent_distribution.map((item, index) => (
                  <IntentCard key={item.intent} item={item} index={index} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, color, trend, trendUp }) {
  const colorClasses = {
    blue: {
      bg: 'bg-gradient-to-br from-blue-500 to-blue-600',
      text: 'text-blue-600',
      iconBg: 'bg-blue-100'
    },
    green: {
      bg: 'bg-gradient-to-br from-green-500 to-green-600',
      text: 'text-green-600',
      iconBg: 'bg-green-100'
    },
    purple: {
      bg: 'bg-gradient-to-br from-purple-500 to-purple-600',
      text: 'text-purple-600',
      iconBg: 'bg-purple-100'
    },
    red: {
      bg: 'bg-gradient-to-br from-red-500 to-red-600',
      text: 'text-red-600',
      iconBg: 'bg-red-100'
    }
  };

  const theme = colorClasses[color];

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 overflow-hidden">
      {/* 顶部彩色条 */}
      <div className={`h-1.5 w-full ${theme.bg}`}></div>

      <div className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className={`p-3 rounded-xl ${theme.iconBg} shadow-sm`}>
            <div className="w-7 h-7">
              {icon}
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-600">{title}</h3>
          </div>
        </div>

        <div className="mb-3">
          <p className="text-4xl font-bold text-gray-900">{value}</p>
        </div>

        {trend && (
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
            trendUp ? 'bg-green-50' : 'bg-red-50'
          }`}>
            <span className={`text-base font-bold ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
              {trendUp ? '↑' : '↓'}
            </span>
            <span className={`text-sm font-semibold ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
              {trend}
            </span>
            <span className="text-xs text-gray-500 ml-1">较上期</span>
          </div>
        )}
      </div>
    </div>
  );
}

function QuickStat({ icon, title, value, color }) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-500',
      gradient: 'from-blue-400 to-blue-600'
    },
    green: {
      bg: 'bg-green-500',
      gradient: 'from-green-400 to-green-600'
    },
    purple: {
      bg: 'bg-purple-500',
      gradient: 'from-purple-400 to-purple-600'
    },
    red: {
      bg: 'bg-red-500',
      gradient: 'from-red-400 to-red-600'
    },
    indigo: {
      bg: 'bg-indigo-500',
      gradient: 'from-indigo-400 to-indigo-600'
    },
    amber: {
      bg: 'bg-amber-500',
      gradient: 'from-amber-400 to-amber-600'
    },
    cyan: {
      bg: 'bg-cyan-500',
      gradient: 'from-cyan-400 to-cyan-600'
    }
  };

  const theme = colorClasses[color];

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 overflow-hidden">
      {/* 左侧彩色条 */}
      <div className={`h-full w-1.5 ${theme.bg}`}></div>

      <div className="p-6 pl-7">
        <div className="flex items-center justify-between mb-3">
          <div className={`p-3 rounded-xl ${theme.bg} bg-opacity-10`}>
            <div className="w-6 h-6">
              {icon}
            </div>
          </div>
        </div>

        <h3 className="text-sm font-semibold text-gray-600 mb-2">{title}</h3>
        <p className={`text-3xl font-bold bg-gradient-to-r ${theme.gradient} bg-clip-text text-transparent`}>
          {value}
        </p>
      </div>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="flex justify-between items-center p-4 bg-white bg-opacity-70 rounded-xl hover:bg-opacity-90 transition-colors shadow-sm border border-gray-100">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <span className="text-lg font-bold text-gray-900">{value}</span>
    </div>
  );
}

function IntentCard({ item, index }) {
  const colors = [
    {
      gradient: 'from-blue-500 to-blue-600',
      bg: 'bg-blue-500'
    },
    {
      gradient: 'from-purple-500 to-purple-600',
      bg: 'bg-purple-500'
    },
    {
      gradient: 'from-pink-500 to-pink-600',
      bg: 'bg-pink-500'
    },
    {
      gradient: 'from-red-500 to-red-600',
      bg: 'bg-red-500'
    },
    {
      gradient: 'from-orange-500 to-orange-600',
      bg: 'bg-orange-500'
    },
    {
      gradient: 'from-amber-500 to-amber-600',
      bg: 'bg-amber-500'
    }
  ];

  const color = colors[index % colors.length];

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 overflow-hidden">
      {/* 顶部彩色条 */}
      <div className={`h-1.5 w-full bg-gradient-to-r ${color.gradient}`}></div>

      <div className="p-6">
        <div className="mb-4">
          <div className={`inline-flex items-center px-3 py-1.5 ${color.bg} bg-opacity-10 rounded-full`}>
            <div className={`w-2 h-2 rounded-full ${color.bg} mr-2`}></div>
            <span className="text-sm font-semibold text-gray-700">{item.intent}</span>
          </div>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold bg-gradient-to-r text-transparent bg-clip-text from-gray-800 to-gray-600">
            {item.count}
          </span>
          <span className="text-sm font-semibold text-gray-500">({item.percentage}%)</span>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;