# Cryptocurrency Trading Platform

This project is a cryptocurrency trading platform that allows users to get buy and sell prices, execute limit orders, and view executed orders.

## Features

- Get buy and sell prices for a given quantity of a cryptocurrency
- Execute limit orders for a given quantity of a cryptocurrency
- View executed orders

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

## Installation

1. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the script:

    ```bash
    python main.py --quantity <float>
    ```

    Example:

    ```bash
    python main.py --quantity 10.0
    ```

    Results will be written to console.

2. Build the server:

    ```bash
    docker-compose up --build
    ```
