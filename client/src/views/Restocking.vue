<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="orderConfirmation" class="confirmation" role="status">
        <strong>{{ t('restocking.orderPlaced') }}</strong>
        <span>{{ t('restocking.orderSummary', { orderNumber: orderConfirmation.order_number, days: orderConfirmation.lead_time_days }) }}</span>
      </div>
      <div v-if="submitError" class="submit-error" role="alert">{{ submitError }}</div>

      <div class="budget-card card">
        <div class="budget-summary">
          <div class="summary-item">
            <div class="summary-label">{{ t('restocking.budget') }}</div>
            <div class="summary-value">{{ formatMoney(budget) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">{{ t('restocking.spent') }}</div>
            <div class="summary-value">{{ formatMoney(spent) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">{{ t('restocking.remaining') }}</div>
            <div class="summary-value">{{ formatMoney(remaining) }}</div>
          </div>
        </div>
        <input
          v-model.number="budget"
          class="budget-slider"
          type="range"
          min="0"
          :max="maxBudget"
          :step="step"
          :disabled="maxBudget === 0"
          :aria-label="t('restocking.budgetSlider')"
          :style="{ '--fill': sliderFill }"
        />
        <div class="slider-bounds">
          <span>{{ formatMoney(0) }}</span>
          <span>{{ formatMoney(maxBudget) }}</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }} ({{ recommended.length }})</h3>
          <button
            class="place-order-btn"
            type="button"
            :disabled="recommended.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.submitting') : t('restocking.placeOrder') }}
          </button>
        </div>
        <div v-if="recommended.length === 0" class="empty-state">
          {{ candidates.length === 0 ? t('restocking.noShortfall') : t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.category') }}</th>
                <th>{{ t('restocking.table.quantity') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommended" :key="item.sku">
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ translateProductName(item.name) }}</td>
                <td>{{ item.category }}</td>
                <td>{{ item.quantity.toLocaleString() }}</td>
                <td>{{ formatMoney(item.unit_cost, 2) }}</td>
                <td><strong>{{ formatMoney(item.cost, 2) }}</strong></td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

const TREND_RANK = { increasing: 2, stable: 1, decreasing: 0 }

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)
    const submitting = ref(false)
    const submitError = ref(null)
    const orderConfirmation = ref(null)

    // Items with a shortfall, ranked by shortfall ratio then trend
    const candidates = computed(() => {
      return forecasts.value
        .map(f => {
          const demand = Number(f.forecasted_demand) || 0
          const stock = Number(f.stock_on_hand) || 0
          const unitCost = Number(f.unit_cost) || 0
          const shortfall = Math.max(0, demand - stock)
          return {
            sku: f.item_sku,
            name: f.item_name,
            category: f.category || '',
            trend: f.trend,
            unit_cost: unitCost,
            quantity: shortfall,
            cost: shortfall * unitCost,
            ratio: demand > 0 ? shortfall / demand : 0
          }
        })
        .filter(i => i.quantity > 0 && i.unit_cost > 0)
        .sort((a, b) => {
          if (b.ratio !== a.ratio) return b.ratio - a.ratio
          return (TREND_RANK[b.trend] ?? 0) - (TREND_RANK[a.trend] ?? 0)
        })
    })

    const totalShortfallCost = computed(() => candidates.value.reduce((sum, i) => sum + i.cost, 0))

    // Step is one tenth of the leading power of ten of the total (e.g. 47,300 -> 1,000)
    const step = computed(() => {
      const total = totalShortfallCost.value
      if (total <= 0) return 1
      return Math.max(1, Math.pow(10, Math.floor(Math.log10(total)) - 1))
    })

    const maxBudget = computed(() => Math.ceil(totalShortfallCost.value / step.value) * step.value)

    // Greedy fill: skip items that do not fit, keep trying cheaper ones
    const recommended = computed(() => {
      let left = Number(budget.value) || 0
      const picked = []
      for (const item of candidates.value) {
        if (item.cost <= left) {
          picked.push(item)
          left -= item.cost
        }
      }
      return picked
    })

    const spent = computed(() => recommended.value.reduce((sum, i) => sum + i.cost, 0))
    const remaining = computed(() => Math.max(0, (Number(budget.value) || 0) - spent.value))
    const sliderFill = computed(() => {
      return maxBudget.value > 0 ? `${Math.min(100, (budget.value / maxBudget.value) * 100)}%` : '0%'
    })

    const formatMoney = (amount, decimals = 0) => {
      return formatCurrencyWithDecimals(amount, currentCurrency.value, decimals)
    }

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        budget.value = Math.round(maxBudget.value / 2 / step.value) * step.value
      } catch (err) {
        error.value = t('restocking.loadFailed') + ': ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (recommended.value.length === 0 || submitting.value) return
      submitting.value = true
      submitError.value = null
      orderConfirmation.value = null
      try {
        orderConfirmation.value = await api.createRestockOrder({
          budget: Number(budget.value),
          items: recommended.value.map(i => ({
            sku: i.sku,
            name: i.name,
            category: i.category,
            quantity: i.quantity,
            unit_cost: i.unit_cost
          }))
        })
      } catch (err) {
        const detail = err.response?.data?.detail
        submitError.value = t('restocking.orderFailed') + ': ' + (typeof detail === 'string' ? detail : err.message)
      } finally {
        submitting.value = false
      }
    }

    // Clear stale confirmation/error once the user changes the budget
    watch(budget, () => {
      submitError.value = null
    })

    onMounted(loadForecasts)

    return {
      t,
      translateProductName,
      loading,
      error,
      budget,
      step,
      maxBudget,
      candidates,
      recommended,
      spent,
      remaining,
      sliderFill,
      submitting,
      submitError,
      orderConfirmation,
      formatMoney,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-card {
  padding: var(--space-5);
  margin-bottom: var(--space-5);
}

.budget-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-5);
}

.summary-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin-top: var(--space-1);
}

.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  border-radius: var(--radius-sm);
  background: linear-gradient(to right, var(--color-accent) var(--fill, 0%), var(--color-border) var(--fill, 0%));
  outline: none;
  cursor: pointer;
}

.budget-slider:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.budget-slider::-webkit-slider-runnable-track {
  height: 8px;
  border-radius: var(--radius-sm);
  background: transparent;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  margin-top: -7px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 3px solid var(--color-accent);
  box-shadow: var(--shadow-md);
  transition: transform var(--transition);
}

.budget-slider:hover::-webkit-slider-thumb {
  transform: scale(1.1);
}

.budget-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 4px var(--color-focus-ring);
}

.budget-slider::-moz-range-track {
  height: 8px;
  border-radius: var(--radius-sm);
  background: var(--color-border);
}

.budget-slider::-moz-range-progress {
  height: 8px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
}

.budget-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 3px solid var(--color-accent);
  box-shadow: var(--shadow-md);
}

.slider-bounds {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.place-order-btn {
  background: var(--color-accent);
  color: var(--color-text-inverse);
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition);
}

.place-order-btn:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

.place-order-btn:disabled {
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.confirmation,
.submit-error {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-5);
  font-size: var(--text-sm);
}

.confirmation {
  background: var(--status-success-bg);
  border: 1px solid var(--status-success-fg);
  color: var(--status-success-fg);
}

.submit-error {
  background: var(--status-danger-bg);
  border: 1px solid var(--status-danger-fg);
  color: var(--status-danger-fg);
}

.empty-state {
  padding: var(--space-6);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
</style>
