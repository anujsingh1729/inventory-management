<template>
  <div class="reports">
    <div class="page-header">
      <h2>{{ t("reports.title") }}</h2>
      <p>{{ t("reports.subtitle") }}</p>
    </div>

    <div v-if="loading" class="loading" role="status" aria-live="polite">
      {{ t("reports.loading") }}
    </div>
    <div v-else-if="error" class="error" role="status" aria-live="polite">
      {{ error }}
    </div>
    <div v-else>
      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("reports.quarterly.title") }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t("reports.quarterly.quarter") }}</th>
                <th>{{ t("reports.quarterly.totalOrders") }}</th>
                <th>{{ t("reports.quarterly.totalRevenue") }}</th>
                <th>{{ t("reports.quarterly.avgOrderValue") }}</th>
                <th>{{ t("reports.quarterly.fulfillmentRate") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="q in quarterlyData" :key="q.quarter">
                <td>
                  <strong>{{ q.quarter }}</strong>
                </td>
                <td>{{ q.total_orders }}</td>
                <td>${{ formatNumber(q.total_revenue) }}</td>
                <td>${{ formatNumber(q.avg_order_value) }}</td>
                <td>
                  <span :class="getFulfillmentClass(q.fulfillment_rate)">
                    {{ q.fulfillment_rate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Monthly Trends Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("reports.monthlyTrend.title") }}</h3>
        </div>
        <div class="chart-container">
          <div class="bar-chart">
            <div
              v-for="month in monthlyData"
              :key="month.month"
              class="bar-wrapper"
            >
              <div class="bar-container">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(month.revenue) + 'px' }"
                  :title="'$' + formatNumber(month.revenue)"
                ></div>
              </div>
              <div class="bar-label">{{ formatMonth(month.month) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-over-Month Comparison -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t("reports.monthlyAnalysis.title") }}</h3>
        </div>
        <div class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t("reports.monthlyAnalysis.month") }}</th>
                <th>{{ t("reports.monthlyAnalysis.orders") }}</th>
                <th>{{ t("reports.monthlyAnalysis.revenue") }}</th>
                <th>{{ t("reports.monthlyAnalysis.change") }}</th>
                <th>{{ t("reports.monthlyAnalysis.growthRate") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(month, index) in monthlyData" :key="month.month">
                <td>
                  <strong>{{ formatMonth(month.month) }}</strong>
                </td>
                <td>{{ month.order_count }}</td>
                <td>${{ formatNumber(month.revenue) }}</td>
                <td>
                  <span
                    v-if="index > 0"
                    :class="
                      getChangeClass(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    "
                  >
                    {{
                      getChangeValue(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td>
                  <span
                    v-if="index > 0"
                    :class="
                      getChangeClass(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    "
                  >
                    {{
                      getGrowthRate(
                        month.revenue,
                        monthlyData[index - 1].revenue,
                      )
                    }}
                  </span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t("reports.summary.totalRevenue") }}</div>
          <div class="stat-value">${{ formatNumber(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">
            {{ t("reports.summary.avgMonthlyRevenue") }}
          </div>
          <div class="stat-value">${{ formatNumber(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t("reports.summary.totalOrders") }}</div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t("reports.summary.bestQuarter") }}</div>
          <div class="stat-value">{{ bestQuarter }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";
import { api } from "../api";
import { useFilters } from "../composables/useFilters";
import { useI18n } from "../composables/useI18n";

export default {
  name: "Reports",
  setup() {
    const { t, currentLocale } = useI18n();
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters,
    } = useFilters();

    const loading = ref(false);
    const error = ref(null);
    const quarterlyData = ref([]);
    const monthlyData = ref([]);

    // BUG 8: computed summary stats derived from reactive data refs
    const totalRevenue = computed(() =>
      monthlyData.value.reduce((sum, m) => sum + m.revenue, 0),
    );

    const avgMonthlyRevenue = computed(() =>
      monthlyData.value.length > 0
        ? totalRevenue.value / monthlyData.value.length
        : 0,
    );

    const totalOrders = computed(() =>
      monthlyData.value.reduce((sum, m) => sum + m.order_count, 0),
    );

    const bestQuarter = computed(() => {
      if (quarterlyData.value.length === 0) return "";
      return (
        quarterlyData.value.reduce(
          (best, q) =>
            q.total_revenue > (best?.total_revenue ?? -Infinity) ? q : best,
          null,
        )?.quarter ?? ""
      );
    });

    // BUG 7: maxRevenue computed once, not inside getBarHeight
    const maxRevenue = computed(() => {
      if (monthlyData.value.length === 0) return 0;
      return Math.max(...monthlyData.value.map((m) => m.revenue));
    });

    // BUG 13: reset error and set loading before try
    const loadData = async () => {
      error.value = null;
      loading.value = true;
      try {
        const filters = getCurrentFilters();
        const [quarterly, monthly] = await Promise.all([
          api.getReportsQuarterly(filters),
          api.getReportsMonthly(filters),
        ]);
        quarterlyData.value = quarterly;
        monthlyData.value = monthly;
      } catch (err) {
        // BUG 12: use locale key; only log err.message to console
        error.value = t("reports.error");
        console.error("Failed to load reports:", err.message);
      } finally {
        loading.value = false;
      }
    };

    // BUG 10: locale-aware number formatting
    const formatNumber = (num) => {
      if (num == null || isNaN(num)) return "0.00";
      return Number(num).toLocaleString(
        currentLocale.value === "ja" ? "ja-JP" : "en-US",
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
      );
    };

    // BUG 11: locale-aware month formatting
    const formatMonth = (monthStr) => {
      if (!monthStr) return "";
      const date = new Date(monthStr + "-01");
      if (isNaN(date.getTime())) return monthStr;
      const locale = currentLocale.value === "ja" ? "ja-JP" : "en-US";
      return date.toLocaleDateString(locale, {
        month: "short",
        year: "numeric",
      });
    };

    // BUG 7: just divides by precomputed maxRevenue
    const getBarHeight = (revenue) => {
      if (maxRevenue.value === 0) return 0;
      return (revenue / maxRevenue.value) * 200;
    };

    const getFulfillmentClass = (rate) => {
      if (rate >= 90) return "badge success";
      if (rate >= 75) return "badge warning";
      return "badge danger";
    };

    const getChangeValue = (current, previous) => {
      const change = current - previous;
      if (change > 0) return "+$" + formatNumber(change);
      if (change < 0) return "-$" + formatNumber(Math.abs(change));
      return "$0.00";
    };

    const getChangeClass = (current, previous) => {
      const change = current - previous;
      if (change > 0) return "positive-change";
      if (change < 0) return "negative-change";
      return "";
    };

    const getGrowthRate = (current, previous) => {
      if (previous === 0) return "N/A";
      const rate = ((current - previous) / previous) * 100;
      const sign = rate > 0 ? "+" : "";
      return sign + rate.toFixed(1) + "%";
    };

    // BUG 4: watch all four filter refs
    watch(
      [selectedPeriod, selectedLocation, selectedCategory, selectedStatus],
      loadData,
    );

    onMounted(loadData);

    return {
      t,
      loading,
      error,
      quarterlyData,
      monthlyData,
      totalRevenue,
      avgMonthlyRevenue,
      totalOrders,
      bestQuarter,
      formatNumber,
      formatMonth,
      getBarHeight,
      getFulfillmentClass,
      getChangeValue,
      getChangeClass,
      getGrowthRate,
    };
  },
};
</script>

<style scoped>
.reports {
  padding: 0;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  margin-bottom: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.card-header {
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  background: var(--color-surface-muted);
  padding: var(--space-3);
  text-align: left;
  font-weight: 600;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
}

.reports-table td {
  padding: var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
}

.reports-table tr:hover td {
  background: var(--color-surface-muted);
}

.chart-container {
  padding: var(--space-5) var(--space-4);
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: var(--space-2);
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
  border-bottom: 1px solid var(--color-border);
}

.bar {
  width: 100%;
  background: var(--color-accent);
  opacity: 0.85;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: opacity var(--transition);
  cursor: pointer;
}

.bar:hover {
  opacity: 1;
}

.bar-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: var(--space-5);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin-top: var(--space-5);
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  border-left: 3px solid var(--color-accent);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
}

.badge {
  padding: var(--space-1) var(--space-3);
  border-radius: 9999px;
  font-size: var(--text-xs);
  font-weight: 600;
}

.badge.success {
  background: var(--status-success-bg);
  color: var(--status-success-fg);
}

.badge.warning {
  background: var(--status-warning-bg);
  color: var(--status-warning-fg);
}

.badge.danger {
  background: var(--status-danger-bg);
  color: var(--status-danger-fg);
}

.positive-change {
  color: var(--color-success);
  font-weight: 600;
}

.negative-change {
  color: var(--color-danger);
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: var(--space-7);
  color: var(--color-text-muted);
}

.error {
  background: var(--status-danger-bg);
  color: var(--status-danger-fg);
  padding: var(--space-4);
  border-radius: var(--radius-sm);
  margin: var(--space-4) 0;
}
</style>
