SET NOCOUNT ON;
IF DB_ID(N'SalesDB') IS NULL
BEGIN
    CREATE DATABASE SalesDB;
END
GO

USE SalesDB;
GO

CREATE TABLE Countries (
    CountryID INT IDENTITY(1,1) PRIMARY KEY,
    CountryName NVARCHAR(50) NULL,
    Continent NVARCHAR(50) NULL
);
GO

CREATE TABLE DateDimension (
    DateID INT IDENTITY(1,1) PRIMARY KEY,
    FullDate DATE NULL,
    Year INT NULL,
    Quarter INT NULL,
    Month INT NULL,
    MonthName NVARCHAR(20) NULL,
    Day INT NULL,
    DayOfWeek NVARCHAR(20) NULL
);
GO

CREATE TABLE Categories (
    CategoryID INT IDENTITY(1,1) PRIMARY KEY,
    CategoryName NVARCHAR(50) NULL,
    ParentCategoryID INT NULL,
    Description NVARCHAR(200) NULL
);
GO

CREATE TABLE Regions (
    RegionID INT IDENTITY(1,1) PRIMARY KEY,
    RegionName NVARCHAR(50) NULL,
    CountryID INT NULL
);
GO

CREATE TABLE Sellers (
    SellerID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName NVARCHAR(50) NULL,
    LastName NVARCHAR(50) NULL,
    Email NVARCHAR(100) NULL,
    Phone NVARCHAR(20) NULL,
    SellerType NVARCHAR(20) NULL,
    RegionID INT NULL,
    HireDate DATETIME NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    UpdatedAt DATETIME NULL
);
GO

CREATE TABLE Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NULL,
    CategoryID INT NULL,
    SellerID INT NULL,
    Price DECIMAL(10,2) NULL,
    CostPrice DECIMAL(10,2) NULL,
    StockQuantity INT NULL,
    Description NVARCHAR(500) NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    UpdatedAt DATETIME NULL
);
GO

CREATE TABLE Customers (
    CustomerID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName NVARCHAR(50) NULL,
    LastName NVARCHAR(50) NULL,
    Email NVARCHAR(100) NULL,
    Phone NVARCHAR(20) NULL,
    Address NVARCHAR(200) NULL,
    CountryID INT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    UpdatedAt DATETIME NULL
);
GO

CREATE TABLE BankAccounts (
    AccountID INT IDENTITY(1,1) PRIMARY KEY,
    AccountNumber NVARCHAR(50) NULL,
    BankName NVARCHAR(100) NULL,
    Currency NVARCHAR(3) NULL,
    Balance DECIMAL(15,2) NULL,
    AccountType NVARCHAR(20) NULL,
    SellerID INT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    UpdatedAt DATETIME NULL
);
GO

CREATE TABLE BankTransactions (
    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
    AccountID INT NULL,
    TransactionDate DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    DateID INT NULL,
    Amount DECIMAL(15,2) NULL,
    TransactionType NVARCHAR(20) NULL,
    Description NVARCHAR(200) NULL,
    Counterparty NVARCHAR(100) NULL,
    ReferenceNumber NVARCHAR(50) NULL,
    SellerID INT NULL
);
GO

CREATE TABLE Orders (
    OrderID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NULL,
    SellerID INT NULL,
    OrderDate DATETIME NOT NULL DEFAULT (GETUTCDATE()),
    DateID INT NULL,
    TotalAmount DECIMAL(10,2) NULL,
    Status NVARCHAR(20) NULL,
    ShippingAddress NVARCHAR(200) NULL,
    CountryID INT NULL,
    PaymentMethod NVARCHAR(50) NULL,
    CreatedAt DATETIME NOT NULL DEFAULT (GETUTCDATE())
);
GO

CREATE TABLE OrderDetails (
    OrderDetailID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NULL,
    ProductID INT NULL,
    Quantity INT NULL,
    UnitPrice DECIMAL(10,2) NULL,
    UnitCostPrice DECIMAL(10,2) NULL,
    Discount DECIMAL(5,2) NOT NULL DEFAULT (0.00)
);
GO

CREATE TABLE Promotions (
    PromotionID INT IDENTITY(1,1) PRIMARY KEY,
    PromotionName NVARCHAR(100) NULL,
    StartDateID INT NULL,
    EndDateID INT NULL,
    DiscountPercentage DECIMAL(5,2) NULL,
    ProductID INT NULL,
    CategoryID INT NULL,
    SellerID INT NULL
);
GO

CREATE UNIQUE INDEX UX_BankAccounts_AccountNumber ON BankAccounts(AccountNumber);
CREATE INDEX IX_BankAccounts_SellerID ON BankAccounts(SellerID);

CREATE INDEX IX_BankTransactions_AccountID ON BankTransactions(AccountID);
CREATE INDEX IX_BankTransactions_DateID ON BankTransactions(DateID);
CREATE INDEX IX_BankTransactions_SellerID ON BankTransactions(SellerID);

CREATE INDEX IX_Categories_ParentCategoryID ON Categories(ParentCategoryID);

CREATE UNIQUE INDEX UX_Customers_Email ON Customers(Email);
CREATE INDEX IX_Customers_CountryID ON Customers(CountryID);

CREATE INDEX IX_OrderDetails_OrderID ON OrderDetails(OrderID);
CREATE INDEX IX_OrderDetails_ProductID ON OrderDetails(ProductID);

CREATE INDEX IX_Orders_CustomerID ON Orders(CustomerID);
CREATE INDEX IX_Orders_SellerID ON Orders(SellerID);
CREATE INDEX IX_Orders_DateID ON Orders(DateID);
CREATE INDEX IX_Orders_CountryID ON Orders(CountryID);

CREATE INDEX IX_Products_CategoryID ON Products(CategoryID);
CREATE INDEX IX_Products_SellerID ON Products(SellerID);

CREATE INDEX IX_Promotions_StartDateID ON Promotions(StartDateID);
CREATE INDEX IX_Promotions_EndDateID ON Promotions(EndDateID);
CREATE INDEX IX_Promotions_ProductID ON Promotions(ProductID);
CREATE INDEX IX_Promotions_CategoryID ON Promotions(CategoryID);
CREATE INDEX IX_Promotions_SellerID ON Promotions(SellerID);

CREATE UNIQUE INDEX UX_Sellers_Email ON Sellers(Email);
CREATE INDEX IX_Sellers_RegionID ON Sellers(RegionID);

CREATE INDEX IX_Regions_CountryID ON Regions(CountryID);
GO

ALTER TABLE Categories
  ADD CONSTRAINT FK_Categories_ParentCategory
  FOREIGN KEY (ParentCategoryID) REFERENCES Categories(CategoryID);
GO

ALTER TABLE Regions
  ADD CONSTRAINT FK_Regions_Countries
  FOREIGN KEY (CountryID) REFERENCES Countries(CountryID);
GO

ALTER TABLE Sellers
  ADD CONSTRAINT FK_Sellers_Regions
  FOREIGN KEY (RegionID) REFERENCES Regions(RegionID);
GO

ALTER TABLE Products
  ADD CONSTRAINT FK_Products_Categories
  FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID);
GO

ALTER TABLE Products
  ADD CONSTRAINT FK_Products_Sellers
  FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID);
GO

ALTER TABLE Customers
  ADD CONSTRAINT FK_Customers_Countries
  FOREIGN KEY (CountryID) REFERENCES Countries(CountryID);
GO

ALTER TABLE BankAccounts
  ADD CONSTRAINT FK_BankAccounts_Sellers
  FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID);
GO

ALTER TABLE BankTransactions
  ADD CONSTRAINT FK_BankTransactions_BankAccounts
  FOREIGN KEY (AccountID) REFERENCES BankAccounts(AccountID);
GO

ALTER TABLE BankTransactions
  ADD CONSTRAINT FK_BankTransactions_DateDimension
  FOREIGN KEY (DateID) REFERENCES DateDimension(DateID);
GO

ALTER TABLE BankTransactions
  ADD CONSTRAINT FK_BankTransactions_Sellers
  FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID);
GO

ALTER TABLE Orders
  ADD CONSTRAINT FK_Orders_Customers
  FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID);
GO

ALTER TABLE Orders
  ADD CONSTRAINT FK_Orders_Sellers
  FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID);
GO

ALTER TABLE Orders
  ADD CONSTRAINT FK_Orders_DateDimension
  FOREIGN KEY (DateID) REFERENCES DateDimension(DateID);
GO

ALTER TABLE Orders
  ADD CONSTRAINT FK_Orders_Countries
  FOREIGN KEY (CountryID) REFERENCES Countries(CountryID);
GO

ALTER TABLE OrderDetails
  ADD CONSTRAINT FK_OrderDetails_Orders
  FOREIGN KEY (OrderID) REFERENCES Orders(OrderID);
GO

ALTER TABLE OrderDetails
  ADD CONSTRAINT FK_OrderDetails_Products
  FOREIGN KEY (ProductID) REFERENCES Products(ProductID);
GO

ALTER TABLE Promotions
  ADD CONSTRAINT FK_Promotions_StartDate
  FOREIGN KEY (StartDateID) REFERENCES DateDimension(DateID);
GO

ALTER TABLE Promotions
  ADD CONSTRAINT FK_Promotions_EndDate
  FOREIGN KEY (EndDateID) REFERENCES DateDimension(DateID);
GO

ALTER TABLE Promotions
  ADD CONSTRAINT FK_Promotions_Products
  FOREIGN KEY (ProductID) REFERENCES Products(ProductID);
GO

ALTER TABLE Promotions
  ADD CONSTRAINT FK_Promotions_Categories
  FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID);
GO

ALTER TABLE Promotions
  ADD CONSTRAINT FK_Promotions_Sellers
  FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID);
GO

ALTER TABLE Regions
  ADD CONSTRAINT FK_Regions_Countries_2
  FOREIGN KEY (CountryID) REFERENCES Countries(CountryID);

GO

SET NOCOUNT OFF;