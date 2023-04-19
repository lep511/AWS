### The Entities are related as follows:

* An Customer can have One or Many Orders
* An Order can contain One or Many Products (OrderLines)
* A Product can be associated with One or Many Orders
* A Supplier can supply One or Many Products

The design allows a Customer to place zero, one or many Orders. An Order can be for one or many Products, and this Product can be associated with zero, one or many Orders (the reason for the Link_OrderProduct table)

When asking questions of the database we may need to know:

1. Which Products have been Ordered by a Customer
2. What date/time was a particular Order dispatched
3. How many open Orders do we have in the system
4. What is the Total Order Cost for a certain Order
5. Which Supplier supplies a particular Product
6. How many of a certain Product do we have in stock
7. What is the mark-up on a certain Product