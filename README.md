# Stock Investment Tracker App - Backend Service

A Python FastApi backend service for tracking stock investments, financial data, and getting AI insights. The app is currently live on [**`ValuIntel.com`**](https://valuintel.com/), while this backend API is on [**`api.ValuIntel.com`**](https://api.valuintel.com/). To view the routes, check out the api's docs here [`api.ValuIntel.com/docs`](https://api.valuintel.com/docs/)

**Built by Value Investor for Value Investors.**

## Features

- **User Authentication**: Secure registration and login system using JWT
- **Financial Data Store**: Input and save financial results of stocks
- **AI Insights**: Get AI insights on the stock based on the inputted data and web search


## Planned Features

- **Portfolio Tracking**: Monitor your stock holdings and performance
- **Personal Reminders**: Push notification/email for buy/sell actions
- **Gain/Loss Analysis**: Track your investment performance with detailed analytics
- **Stock Search**: AI-powered search for stocks that fit value investment criteria
- **Test Suites**: Because it is important


## Tech Stack

- **Backend**: Python 3, FastAPI
- **Database**: PostgreSQL (via SQLAlchemy async)
- **Authentication**: JWT (JSON Web Tokens)
- **AI Integration**: OpenAI API
- **ORM**: SQLAlchemy 2.x (async)
- **Server**: Uvicorn

## Run the App

### Prerequisites

- Python3.11
- Although any Front End app can do, this app (https://github.com/Izzat1098/stocks_app_frontend) is the one designed to work with this backend

### Installation

1. Clone the repository:

2. Create python's virtual environment (optional but highly recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables by creating an `.env` file and adding these lines:
- APP_ENV=development
- SECRET_KEY=`yoursecretkey`
- DATABASE_URL=`yourpostgresqldburl`
- OPENAI_API_KEY=`youropenaiapikey`
- CORS_ORIGINS=http://localhost:3000,http://localhost:3001

5. Start the development server:
```bash
python -m backend
```

The app can then be accessed at [http://localhost:8000](http://localhost:8000)


## Deployment

### Development
Currently, the app is hosted on render.com as web service which is super easy (there is no need to build the app, just link the github repo to the service). The database is also hosted on render as PostgreSQL database. Of course, you can use any other hosting services too. More information on this can be found on the service's docs or you can also contact me.