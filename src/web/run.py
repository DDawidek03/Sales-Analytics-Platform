from app import app

if __name__ == '__main__':
    print("Starting GlobalVista Flask Server...")
    print("Visit: http://127.0.0.1:5000")
    print("Dashboard: http://127.0.0.1:5000/index")
    app.run(debug=True, host='127.0.0.1', port=5000)
