from operator import contains
import os
from urllib import response
from datetime import date
from flask import Flask, session, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import dynamodb_handler as dynamodb

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
  
# MAIN
@app.route('/')
@app.route("/dashboard")
def dashboard():
    return render_template("home.html", home=True)

@app.route("/viewaccount" , methods=["GET", "POST"])
def viewaccount():
    if 'user' not in session:
        return redirect(url_for('login'))        
    if session['usert']=="customer":
        if request.method == "POST":
            acc_id = request.form.get("acc_id")
            cust_id = request.form.get("cust_id")
            items = {}
            if (acc_id != ""):
                response = dynamodb.getAccountDetailsByAcctId(int(acc_id))
                items=response['Items']
            else:
                items = dynamodb.getAccountDetailsByCustId(cust_id)
            
            print('data', items)
            if items:
                return render_template('viewaccount.html', viewaccount=True, data=items)
        
            flash("Account not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('viewaccount.html', viewaccount=True)


@app.route("/viewaccountstatus" , methods=["GET", "POST"])
def viewaccountstatus():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('viewaccountstatus.html', viewaccountstatus=True)

# Code for deposit amount 
@app.route('/deposit',methods=['GET','POST'])
@app.route('/deposit/<acc_id>',methods=['GET','POST'])
def deposit(acc_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="customer":
        print('in get',acc_id)
        if acc_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                print('in post deposit', acc_id)
                amount = request.form.get("amount")
                print('amount', amount)
                response=dynamodb.getAccountDetailsByAcctId(int(acc_id))
                if response['Items'] is not None:
                    updatedBalance = int(amount) + int(response['Items'][0]['balance'])
                    result=dynamodb.updateAcctBalance(int(acc_id), updatedBalance)
                    flash(f"{amount} Amount deposited into account: {acc_id} successfully.",'success')
                    dynamodb.insertTransactions(acc_id,"Amount Deposited",amount)
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                response = dynamodb.getAccountDetailsByAcctId(int(acc_id))
                if response['Items'] is not None:
                    return render_template('deposit.html', deposit=True, data=response['Items'])
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('viewaccount'))

# Code for withdraw amount 
@app.route('/withdraw',methods=['GET','POST'])
@app.route('/withdraw/<acc_id>',methods=['GET','POST'])
def withdraw(acc_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="customer":
        if acc_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                amount = request.form.get("amount")
                response=dynamodb.getAccountDetailsByAcctId(int(acc_id))
                if response['Items'] is not None:
                    if int(response['Items'][0]['balance'])>=int(amount):
                        updatedBalance =  int(response['Items'][0]['balance'])-int(amount)
                        result=dynamodb.updateAcctBalance(int(acc_id), updatedBalance)
                        flash(f"{amount} Amount withdrawn from account: {acc_id} successfully.",'success')
                        dynamodb.insertTransactions(acc_id,"Amount withdrawn",amount)
                    else:
                        flash(f"Account doesn't have sufficient Balance.",'success')
                        return redirect(url_for('viewaccount'))
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                response = dynamodb.getAccountDetailsByAcctId(int(acc_id))
                if response['Items'] is not None:
                    return render_template('withdraw.html', deposit=True, data=response['Items'])
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('viewaccount'))

# Code for transfer amount using transact_items
@app.route('/transfer',methods=['GET','POST'])
@app.route('/transfer/<cust_id>',methods=['GET','POST'])
def transfer(cust_id=None):
    print(cust_id)
    global src_data
    global trg_data
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert']=="customer":
        if cust_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == 'POST':
                src_type = request.form.get("src_type")
                trg_type = request.form.get("trg_type")
                amount = int(request.form.get("amount"))
                if src_type != trg_type:
                    response = dynamodb.getAccountDetailsByCustId(cust_id)
                    print('transfer',response)
                    for i in response: 
                        res = []
                        for j in i:
                            print('j is', i[j])
                            res.append(i[j])
                        if str('savings') in res:
                            if str('savings')==src_type:
                                src_data = i
                            else:
                                trg_data = i

                        if str('checking') in res:
                            if str('checking')==trg_type:
                                trg_data = i
                            else:
                                src_data = i
                    print(src_data)                         
                    if src_data is not None and trg_data is not None:
                        if src_data['balance'] > amount:
                            src_balance = src_data['balance'] - amount
                            trg_balance = trg_data['balance'] + amount
                            response = dynamodb.transactionUpdate(src_data,trg_data,src_balance,trg_balance,amount)
                            flash(f"{amount} Amount updated into account: {src_data['acc_id']} successfully.",'success')
                            flash(f"{amount} Amount updated into account:  {trg_data['acc_id']} successfully.",'success')
                            flash(f"Amount transferred to {trg_data['acc_id']} from {src_data['acc_id']} successfully",'success')
                        else:
                            flash("Insufficient amount to transfer.","danger")                            
                    else:
                        flash("Accounts not found","danger")
                else:
                    flash("Can't Transfer amount to same account.",'warning')
            else:
                data = dynamodb.getAccountDetailsByCustId(cust_id)
                if data and len(data) == 2:
                    return render_template('transfer.html', deposit=True, cust_id=cust_id)
                else:
                    flash("Data Not found or Invalid Customer ID",'danger')
                    return redirect(url_for('viewaccount'))

    return redirect(url_for('viewaccount'))


# code for view account statement based on the account id
# Using number of last transaction
@app.route("/statement" , methods=["GET", "POST"])
def statement():
    if 'user' not in session:
        return redirect(url_for('login'))    
    if session['usert']=="customer":
        if request.method == "POST":
            acc_id = request.form.get("acc_id")
            number = request.form.get("number")
            flag = request.form.get("Radio")
            if flag=="red":
                data = dynamodb.getTransactions(int(acc_id), number)
            if data:
                print(data)
                return render_template('statement.html', statement=True, data=data['Items'], acc_id=acc_id)
            else:
                flash("No Transactions", 'danger')
                return redirect(url_for('dashboard'))
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('statement.html', statement=True)

# route for 404 error
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html") 

# Logout 
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        usern = request.form.get("username").upper()
        passw = request.form.get("password")

        response = dynamodb.userLogin(usern)
        if response is not None:
            if (response['Item']['password']==passw):
                session['user'] = usern
                session['namet'] = response['Item']['name']
                session['usert'] = response['Item']['user_type']
                flash(f"{response['Item']['name'].capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        flash("Sorry, Username or password not match.","danger")
    return render_template("login.html", login=True)

    
# Main
if __name__ == '__main__':
   # app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
