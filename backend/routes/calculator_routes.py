from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db

calculator_bp = Blueprint('calculator', __name__, url_prefix='/calculator')

@calculator_bp.route('/', methods=['GET'])
def index():
    user_id = session.get('user_id')
    saved_calculations = []
    if user_id:
        saved_calculations = query_db(
            "SELECT * FROM profit_calculations WHERE user_id = ? ORDER BY created_at DESC LIMIT 15",
            (user_id,)
        )
    return render_template('calculator/index.html', saved_calculations=saved_calculations)

@calculator_bp.route('/save', methods=['POST'])
def save_calculation():
    user_id = session.get('user_id')
    data = request.get_json(silent=True) or request.form

    crop_name = data.get('crop_name', 'General Crop').strip()
    title = data.get('calculation_title', f"{crop_name} Season Plan").strip()
    land_area = float(data.get('land_area', 1.0))
    land_unit = data.get('land_unit', 'Acre')
    expected_yield = float(data.get('expected_yield', 0.0))
    yield_unit = data.get('yield_unit', 'Quintal')
    expected_price = float(data.get('expected_price', 0.0))

    # Costs
    seeds_cost = float(data.get('seeds_cost', 0.0))
    fertilizer_cost = float(data.get('fertilizer_cost', 0.0))
    pesticide_cost = float(data.get('pesticide_cost', 0.0))
    labour_cost = float(data.get('labour_cost', 0.0))
    irrigation_cost = float(data.get('irrigation_cost', 0.0))
    transport_cost = float(data.get('transport_cost', 0.0))
    other_expenses = float(data.get('other_expenses', 0.0))

    total_expenses = seeds_cost + fertilizer_cost + pesticide_cost + labour_cost + irrigation_cost + transport_cost + other_expenses
    expected_revenue = expected_yield * expected_price
    expected_profit = expected_revenue - total_expenses

    # Normalize to acre for per-acre metric
    acre_factor = 1.0
    if land_unit == 'Hectare':
        acre_factor = 2.471
    elif land_unit == 'Bigha':
        acre_factor = 0.625
    total_acres = max(0.1, land_area * acre_factor)
    profit_per_acre = round(expected_profit / total_acres, 2)

    calc_id = execute_db(
        """INSERT INTO profit_calculations 
           (user_id, calculation_title, crop_name, land_area, land_unit, expected_yield, yield_unit,
            expected_price, seeds_cost, fertilizer_cost, pesticide_cost, labour_cost,
            irrigation_cost, transport_cost, other_expenses, total_expenses,
            expected_revenue, expected_profit, profit_per_acre)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, title, crop_name, land_area, land_unit, expected_yield, yield_unit,
         expected_price, seeds_cost, fertilizer_cost, pesticide_cost, labour_cost,
         irrigation_cost, transport_cost, other_expenses, total_expenses,
         expected_revenue, expected_profit, profit_per_acre)
    )

    if request.is_json:
        return jsonify({
            'success': True,
            'id': calc_id,
            'total_expenses': total_expenses,
            'expected_revenue': expected_revenue,
            'expected_profit': expected_profit,
            'profit_per_acre': profit_per_acre,
            'message': 'Calculation saved to farm records.'
        })

    flash("Crop profit estimation saved to your history!", "success")
    return redirect(url_for('calculator.index'))

@calculator_bp.route('/delete/<int:calc_id>', methods=['POST'])
def delete_calculation(calc_id):
    user_id = session.get('user_id')
    if user_id:
        execute_db("DELETE FROM profit_calculations WHERE id = ? AND user_id = ?", (calc_id, user_id))
        flash("Record deleted.", "info")
    return redirect(url_for('calculator.index'))
