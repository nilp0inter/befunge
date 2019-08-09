package main

import (
	"testing"
)

func TestStack(t *testing.T) {
	var s Stack

	if s.Pop() != 0 {
		t.Error("Empty stack should pop 0")
	}

	s.Push(5)
	s.Push(10)
	if s.Pop() != 10 || s.Pop() != 5 {
		t.Error("Pop should get values at inverse insertion order")
	}

	if s.Pop() != 0 {
		t.Error("Empty stack should pop 0")
	}
}

func TestGridCorners(t *testing.T) {
	tests := [][2]State{
		// Top Left
		{State{X: 0, Y: 0, Dir: Up}, State{X: 0, Y: 24, Dir: Up}},
		{State{X: 0, Y: 0, Dir: Left}, State{X: 79, Y: 0, Dir: Left}},
		{State{X: 0, Y: 0, Dir: Right}, State{X: 1, Y: 0, Dir: Right}},
		{State{X: 0, Y: 0, Dir: Down}, State{X: 0, Y: 1, Dir: Down}},

		// Top Right
		{State{X: 79, Y: 0, Dir: Up}, State{X: 79, Y: 24, Dir: Up}},
		{State{X: 79, Y: 0, Dir: Left}, State{X: 78, Y: 0, Dir: Left}},
		{State{X: 79, Y: 0, Dir: Right}, State{X: 0, Y: 0, Dir: Right}},
		{State{X: 79, Y: 0, Dir: Down}, State{X: 79, Y: 1, Dir: Down}},

		// Bottom Left
		{State{X: 0, Y: 24, Dir: Up}, State{X: 0, Y: 23, Dir: Up}},
		{State{X: 0, Y: 24, Dir: Left}, State{X: 79, Y: 24, Dir: Left}},
		{State{X: 0, Y: 24, Dir: Right}, State{X: 1, Y: 24, Dir: Right}},
		{State{X: 0, Y: 24, Dir: Down}, State{X: 0, Y: 0, Dir: Down}},

		// Bottom Right
		{State{X: 79, Y: 24, Dir: Up}, State{X: 79, Y: 23, Dir: Up}},
		{State{X: 79, Y: 24, Dir: Left}, State{X: 78, Y: 24, Dir: Left}},
		{State{X: 79, Y: 24, Dir: Right}, State{X: 0, Y: 24, Dir: Right}},
		{State{X: 79, Y: 24, Dir: Down}, State{X: 79, Y: 0, Dir: Down}},
	}

	for _, c := range tests {
		s, e := c[0], c[1]
		s.Advance()
		if s.X != e.X || s.Y != e.Y {
			t.Errorf("Going %v failed, ended up in (%d, %d) instead of (%d, %d)", s.Dir, s.X, s.Y, e.X, e.Y)
		}
	}
}
