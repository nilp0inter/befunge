package main

import (
	"fmt"
	"os"
	"strings"
)

type Direction int

const (
	Right = iota
	Down
	Left
	Up
)

const (
	WIDTH  = 80
	HEIGHT = 25
)

type Stack struct {
	elems []byte
	top   uint
}

func (s *Stack) Pop() byte {
	if s.top == 0 {
		return byte(0)
	} else {
		s.top -= 1
		return s.elems[s.top]
	}
}

func (s *Stack) Push(e byte) {
	if s.top == uint(len(s.elems)) {
		s.elems = append(s.elems, e)
		s.top += 1
	} else {
		s.top += 1
		s.elems[s.top] = e
	}
}

type State struct {
	X     uint8
	Y     uint8
	Dir   Direction
	Ascii bool
	Grid  [HEIGHT][WIDTH]byte
	Stack Stack
}

func (s *State) String() string {
	var rows [HEIGHT]string
	var cells [WIDTH]string
	for y, row := range s.Grid {
		for x, cell := range row {
			if cell >= 32 && cell <= 176 { // Printable ASCII
				cells[x] = string(cell)
			} else {
				cells[x] = " "
			}
		}
		rows[y] = strings.Join(cells[:], "")
	}
	return strings.Join(rows[:], "\n")
}

func (s *State) Advance() {
	switch s.Dir {
	case Right:
		s.X = (s.X + 1) % WIDTH
	case Down:
		s.Y = (s.Y + 1) % HEIGHT
	case Left:
		if s.X == 0 {
			s.X = WIDTH - 1
		} else {
			s.X -= 1
		}
	case Up:
		if s.Y == 0 {
			s.Y = HEIGHT - 1
		} else {
			s.Y -= 1
		}
	}
}

func (s *State) Fetch() byte {
	return s.Grid[s.Y][s.X]
}

func (s *State) Step() {
	if s.Ascii {
		if cell := s.Fetch(); cell == byte('"') {
			s.Ascii = false
		} else {
			s.Stack.Push(cell)
		}
		s.Advance()
	} else {
		switch s.Fetch() {
		case byte('>'):
			s.Dir = Right
		case byte('v'):
			s.Dir = Down
		case byte('<'):
			s.Dir = Left
		case byte('^'):
			s.Dir = Up
		case byte('"'):
			s.Ascii = true
		case byte('.'):
			fmt.Printf("%+q", s.Stack.Pop())
		case byte(','):
			fmt.Printf("%d", s.Stack.Pop())
		}
		s.Advance()
	}
}

func (s *State) Debug() {
	for {
		fmt.Println(s.X, s.Y)
		s.Step()
	}
}

func main() {
	var state State
	if len(os.Args) != 2 {
		fmt.Println("Usage:", os.Args[0], "<program>")
		os.Exit(1)
	}
	state.Debug()

	// state.Dir = Up
	// for i := 0; i < 100; i++ {
	// 	fmt.Println(state.X, state.Y)
	// 	state.Advance()
	// }

	// fmt.Println(state.Stack)
	// fmt.Println(state.Stack.Pop())
	// state.Stack.Push(byte(5))
	// fmt.Println(state.Stack)
	// state.Stack.Push(byte(10))
	// fmt.Println(state.Stack)
	// fmt.Println(state.Stack.Pop())
	// fmt.Println(state.Stack.Pop())
	// fmt.Println(state.Stack.Pop())
}
