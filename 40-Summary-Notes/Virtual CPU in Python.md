---
category: "Technical"
tags:
  - Python
  - CPU
  - virtualization
  - computer-architecture
topics:
  - "Virtual Machines"
  - "Computer Architecture"
  - "Python Programming"
---
# Virtual CPU in Python

This note summarizes discussions and code examples for creating a virtual CPU in Python.

## Concept

A virtual CPU simulates the behavior of a central processing unit in software, allowing for the execution of programs and manipulation of registers and memory.

## Simplified 8-bit CPU Implementation

The provided example demonstrates a basic 8-bit virtual CPU with the following components:

-   **Registers:** 8 general-purpose registers.
-   **Memory:** 256 bytes of memory.
-   **Program Counter:** Points to the current instruction.
-   **Instructions:**
    -   `MOV` (0x1): Move operand to Register 0.
    -   `ADD` (0x2): Add operand to Register 0.
    -   `SUB` (0x3): Subtract operand from Register 0.
    -   `HALT` (0x4): Stop CPU execution.

## Python Code Example

```python
class VirtualCPU:
    def __init__(self):
        self.registers = [0] * 8  # 8 general-purpose registers
        self.memory = [0] * 256   # 256 bytes of memory
        self.program_counter = 0   # Program counter pointing to the current instruction

    def load_program(self, program):
        self.memory[:len(program)] = program

    def fetch(self):
        instruction = self.memory[self.program_counter]
        self.program_counter += 1
        return instruction

    def execute(self, instruction):
        opcode = (instruction & 0xF0) >> 4
        operand = instruction & 0x0F

        if opcode == 0x1:  # MOV instruction
            self.registers[0] = operand
        elif opcode == 0x2:  # ADD instruction
            self.registers[0] += operand
        elif opcode == 0x3:  # SUB instruction
            self.registers[0] -= operand
        elif opcode == 0x4:  # HALT instruction
            return True  # Halt the CPU

        return False  # Continue execution

    def run(self):
        while True:
            instruction = self.fetch()
            halt = self.execute(instruction)
            if halt:
                break

# Example program: MOV 5 to register 0, ADD 3 to register 0, HALT
program = [0x10, 0x50, 0x20, 0x30, 0x40]

cpu = VirtualCPU()
cpu.load_program(program)
cpu.run()

print("Register 0 value:", cpu.registers[0])

# New program: MOV 5 to register 0, MOV 3 to register 1, ADD register 1 to register 0, HALT
new_program = [0x10, 0x50, 0x11, 0x30, 0x20, 0x01, 0x40]

cpu = VirtualCPU()
cpu.load_program(new_program)
cpu.run()

print("Register 0 value:", cpu.registers[0])
print("Register 1 value:", cpu.registers[1])
```

## Related Documents

- [[30-All-Notes/Virtual_CPU_in_Python.md]]

## Related Notes

- [[Python Technical Notes]]
