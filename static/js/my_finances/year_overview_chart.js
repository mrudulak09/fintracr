$(document).ready(function () {
    // Load financial summary data
    loadFinancialSummary();

    // Load existing charts
    $.get("/my_finances/get_year_chart?balance_type=current", function (res) {
        line_chart(res, 'year_chart_canvas')
    });

    $.get("/my_finances/get_income_or_outcome_by_type?get_what=income&summary_type=year_overview", function (res) {
        doughnut_chart(res, 'income_by_type')
    });

    $.get("/my_finances/get_income_or_outcome_by_type?get_what=outcome&summary_type=year_overview", function (res) {
        doughnut_chart(res, 'outcome_by_type')
        // After loading outcome data, populate top expenses table
        populateTopExpenses(res);
    });

    $.get("/my_finances/get_year_chart?balance_type=savings", function (res) {
        line_chart(res, 'savings_year')
    });
    
    // Load monthly comparison data
    loadMonthlyComparison();
})

// Function to load financial summary data
function loadFinancialSummary() {
    // This would normally get data from the server, using placeholder data for now
    // In a real implementation, you would fetch this data from your backend
    
    // Format currency values
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR'}).format(value);
    };
    
    // Example annual values (replace with actual API calls)
    const annualIncome = 1250000;
    const annualExpenses = 950000;
    const netWorthChange = 300000;
    const savingsRate = ((annualIncome - annualExpenses) / annualIncome * 100).toFixed(1);
    
    // Update DOM elements
    $('#total_annual_income').text(formatCurrency(annualIncome));
    $('#total_annual_expenses').text(formatCurrency(annualExpenses));
    $('#net_worth_change').text(formatCurrency(netWorthChange));
    $('#savings_rate').text(savingsRate + '%');
    $('#savings_progress').css('width', savingsRate + '%').attr('aria-valuenow', savingsRate);
    $('#savings_rate_card').text(savingsRate + '%');
}

// Function to populate top expenses table
function populateTopExpenses(data) {
    const tbody = $('#top_expenses_body');
    tbody.empty();
    
    // Sort data by amount in descending order
    const sortedData = [...data.data].map((amount, index) => ({
        category: data.labels[index],
        amount: amount
    })).sort((a, b) => b.amount - a.amount);
    
    // Calculate total
    const total = sortedData.reduce((sum, item) => sum + item.amount, 0);
    
    // Take top 5 expenses
    const topExpenses = sortedData.slice(0, 5);
    
    // Format currency values
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR'}).format(value);
    };
    
    // Add rows to table
    topExpenses.forEach(item => {
        const percent = ((item.amount / total) * 100).toFixed(1);
        const trendIcon = getRandomTrendIcon(); // In real app, calculate actual trend
        
        tbody.append(`
            <tr>
                <td>${item.category}</td>
                <td>${formatCurrency(item.amount)}</td>
                <td>${percent}%</td>
                <td>${trendIcon}</td>
            </tr>
        `);
    });
}

// Helper function to get a random trend icon (for demo purposes)
function getRandomTrendIcon() {
    const trends = [
        '<i class="fas fa-arrow-up text-danger"></i> 2%',
        '<i class="fas fa-arrow-down text-success"></i> 3%',
        '<i class="fas fa-equals text-info"></i> 0%'
    ];
    return trends[Math.floor(Math.random() * trends.length)];
}

// Function to load and display monthly income vs expenses comparison
function loadMonthlyComparison() {
    // Example data - in a real implementation, you would fetch this from your backend
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        incomeData: [85000, 82000, 87000, 84000, 90000, 89000, 92000, 95000, 98000, 100000, 102000, 105000],
        expenseData: [65000, 68000, 70000, 72000, 76000, 79000, 75000, 82000, 77000, 80000, 84000, 86000]
    };
    
    // Create chart
    let canvas = $('#monthly_comparison_chart');
    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Income',
                    data: data.incomeData,
                    backgroundColor: 'rgba(28, 200, 138, 0.6)',
                    borderColor: 'rgba(28, 200, 138, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Expenses',
                    data: data.expenseData,
                    backgroundColor: 'rgba(231, 74, 59, 0.6)',
                    borderColor: 'rgba(231, 74, 59, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-IN', {
                                style: 'currency', 
                                currency: 'INR',
                                maximumSignificantDigits: 3
                            }).format(value);
                        }
                    }
                }
            }
        }
    };
    new Chart(canvas, config);
}