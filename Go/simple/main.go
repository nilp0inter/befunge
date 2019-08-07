package main

import (
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"
)

type Direction int

const (
	Right Direction = iota
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
		cell := s.Fetch()
		switch cell {
		case byte('+'):
			s.Stack.Push(s.Stack.Pop() + s.Stack.Pop())
		case byte('-'):
			a := s.Stack.Pop()
			b := s.Stack.Pop()
			s.Stack.Push(b - a)
		case byte('*'):
			s.Stack.Push(s.Stack.Pop() * s.Stack.Pop())
		case byte('/'):
			a := s.Stack.Pop()
			b := s.Stack.Pop()
			s.Stack.Push(b / a)
		case byte('%'):
			a := s.Stack.Pop()
			b := s.Stack.Pop()
			s.Stack.Push(b % a)
		case byte('!'):
			if a := s.Stack.Pop(); a == 0 {
				s.Stack.Push(1)
			} else {
				s.Stack.Push(0)
			}
		case byte('`'):
			a := s.Stack.Pop()
			b := s.Stack.Pop()
			if b > a {
				s.Stack.Push(1)
			} else {
				s.Stack.Push(0)
			}
		case byte('>'):
			s.Dir = Right
		case byte('<'):
			s.Dir = Left
		case byte('^'):
			s.Dir = Up
		case byte('v'):
			s.Dir = Down
		case byte('?'):
			dirs := []Direction{Right, Down, Left, Up}
			s.Dir = dirs[rand.Intn(len(dirs))]
		case byte('_'):
			if s.Stack.Pop() == 0 {
				s.Dir = Right
			} else {
				s.Dir = Left
			}
		case byte('|'):
			if s.Stack.Pop() == 0 {
				s.Dir = Down
			} else {
				s.Dir = Up
			}
		case byte('"'):
			s.Ascii = true
		case byte(':'):
			a := s.Stack.Pop()
			s.Stack.Push(a)
			s.Stack.Push(a)
		case byte('\\'):
			a := s.Stack.Pop()
			b := s.Stack.Pop()
			s.Stack.Push(a)
			s.Stack.Push(b)
		case byte('$'):
			s.Stack.Pop()
		case byte('.'):
			fmt.Printf("%d", s.Stack.Pop())
		case byte(','):
			fmt.Printf("%+q", s.Stack.Pop())
		case byte('#'):
			s.Advance()
		case byte('g'):
			y := s.Stack.Pop()
			x := s.Stack.Pop()
			if x < WIDTH && y < HEIGHT {
				s.Stack.Push(s.Grid[y][x])
			} else {
				s.Stack.Push(0)
			}
		case byte('p'):
			y := s.Stack.Pop()
			x := s.Stack.Pop()
			v := s.Stack.Pop()
			if x < WIDTH && y < HEIGHT {
				s.Grid[y][x] = v
			}
		case byte('&'):
			var i byte
			for {
				_, err := fmt.Scanf("%d", &i)
				if err != nil {
					break
				}
			}
			s.Stack.Push(i)
		case byte('~'):
			var i byte
			for {
				_, err := fmt.Scanf("%c", &i)
				if err != nil {
					break
				}
			}
			s.Stack.Push(i)
		case byte('@'):
			os.Exit(0)
		default:
			if cell >= byte('0') && cell <= byte('9') {
				s.Stack.Push(cell - byte('0'))
			}
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
	rand.Seed(time.Now().UnixNano())
	state.Debug()
}
