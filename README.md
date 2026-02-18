# Tetris Autoplayer

An automated Tetris player implemented in Python.  
The project focuses on decision-making logic for selecting optimal piece placements based on the current board state.

## Overview
This project implements a Tetris autoplayer that evaluates possible moves for each incoming piece and selects the action that optimizes a heuristic score. The goal is to play Tetris autonomously by minimizing holes, managing stack height, and maximizing line clears.

The project was built as a standalone experiment in algorithmic decision-making and game logic.

## Key Features
- Rule-based decision engine for move selection
- Board evaluation using heuristic scoring
- Modular structure for readability and experimentation
- Designed to be easily extendable with improved heuristics or learning-based approaches

## Project Structure
Tetris autoplayer/
├── player.py
├── README.md
└── requirements.txt

## How It Works
For each incoming Tetris piece:
1. All valid placements are simulated
2. Each resulting board state is scored using heuristics such as:
   - number of holes
   - aggregate column height
   - completed lines
   - surface roughness
3. The move with the best score is selected and executed

## Requirements
- Python 3.x

## Usage
This project is intended to be run in conjunction with a Tetris game environment or simulator that calls the `player.py` logic.

## Limitations
- Heuristic-based (no machine learning)
- Performance depends on the quality of the scoring function
- Assumes a compatible Tetris game interface

## Future Improvements
- Reinforcement learning–based policy
- Adaptive heuristic weights
- Support for different Tetris rule variants

## Author
Developed as a personal project to explore game AI and algorithmic decision-making.
