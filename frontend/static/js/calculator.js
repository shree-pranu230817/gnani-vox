/**
 * UZHAVAR AI - Crop Profit Calculator Engine
 */

document.addEventListener('DOMContentLoaded', function () {
    const calcForm = document.getElementById('profitCalcForm');
    if (!calcForm) return;

    const expenseInputs = [
        'seeds_cost', 'fertilizer_cost', 'pesticide_cost', 
        'labour_cost', 'irrigation_cost', 'transport_cost', 'other_expenses'
    ];

    let expenseChart = null;

    function recalculate() {
        let totalExpenses = 0;
        const expenseValues = [];

        expenseInputs.forEach(id => {
            const input = document.getElementById(id);
            const val = parseFloat(input ? input.value : 0) || 0;
            totalExpenses += val;
            expenseValues.push(val);
        });

        const landArea = parseFloat(document.getElementById('land_area')?.value) || 1;
        const landUnit = document.getElementById('land_unit')?.value || 'Acre';
        const expectedYield = parseFloat(document.getElementById('expected_yield')?.value) || 0;
        const expectedPrice = parseFloat(document.getElementById('expected_price')?.value) || 0;

        const expectedRevenue = expectedYield * expectedPrice;
        const netProfit = expectedRevenue - totalExpenses;

        let acreFactor = 1.0;
        if (landUnit === 'Hectare') acreFactor = 2.471;
        else if (landUnit === 'Bigha') acreFactor = 0.625;
        const totalAcres = Math.max(0.1, landArea * acreFactor);
        const profitPerAcre = netProfit / totalAcres;

        const roi = totalExpenses > 0 ? ((netProfit / totalExpenses) * 100) : 0;
        const breakEvenPrice = expectedYield > 0 ? (totalExpenses / expectedYield) : 0;

        // Update UI
        const elTotalExpenses = document.getElementById('resTotalExpenses');
        const elRevenue = document.getElementById('resRevenue');
        const elProfit = document.getElementById('resProfit');
        const elProfitAcre = document.getElementById('resProfitPerAcre');
        const elRoi = document.getElementById('resRoi');
        const elBreakEven = document.getElementById('resBreakEven');

        if (elTotalExpenses) elTotalExpenses.textContent = `₹${totalExpenses.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        if (elRevenue) elRevenue.textContent = `₹${expectedRevenue.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        
        if (elProfit) {
            elProfit.textContent = `₹${netProfit.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            elProfit.style.color = netProfit >= 0 ? '#1b5e20' : '#dc2626';
        }

        if (elProfitAcre) {
            elProfitAcre.textContent = `₹${profitPerAcre.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            elProfitAcre.style.color = profitPerAcre >= 0 ? '#1b5e20' : '#dc2626';
        }

        if (elRoi) {
            elRoi.textContent = `${roi.toFixed(1)}%`;
            elRoi.style.color = roi >= 0 ? '#1b5e20' : '#dc2626';
        }

        if (elBreakEven) {
            elBreakEven.textContent = `₹${breakEvenPrice.toFixed(2)}`;
        }

        updateChart(expenseValues);
    }

    function updateChart(data) {
        const ctx = document.getElementById('expenseChart');
        if (!ctx) return;

        if (typeof Chart === 'undefined') return;

        const labels = ['Seeds', 'Fertilizers', 'Pesticides', 'Labour', 'Irrigation', 'Transport', 'Others'];
        const colors = ['#2e7d32', '#43a047', '#f59e0b', '#3b82f6', '#06b6d4', '#8b5cf6', '#64748b'];

        if (expenseChart) {
            expenseChart.data.datasets[0].data = data;
            expenseChart.update();
        } else {
            expenseChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                    }
                }
            });
        }
    }

    // Attach listeners to all inputs
    const allInputs = calcForm.querySelectorAll('input, select');
    allInputs.forEach(input => {
        input.addEventListener('input', recalculate);
        input.addEventListener('change', recalculate);
    });

    // Initial calculation
    recalculate();
});
