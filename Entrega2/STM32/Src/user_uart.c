#include <stdint.h>
#include "main.h"
#include "user_uart.h"

// UART1 initialization function
void USER_UART1_Init(void) {
	// Enable GPIOA and USART1 peripheral clocks
	RCC->IOPENR |= (0x1UL << 0U);      // Enable GPIOA clock
	RCC->APBENR2 |= (0x1UL << 14U);    // Enable USART1 clock

	// Configure PA9 (TX) as Alternate Function 1, Push-Pull, No Pull-up/down
	GPIOA->AFRH &= ~(0xEUL << 4U);     // Clear alternate function bits for PA9
	GPIOA->AFRH |= (0x1UL << 4U);      // Set AF1 for PA9
	GPIOA->PUPDR &= ~(0x3UL << 18U);   // No pull-up, no pull-down for PA9
	GPIOA->OTYPER &= ~(0x1UL << 9U);   // Push-pull for PA9
	GPIOA->MODER &= ~(0x3UL << 18U);   // Clear mode bits for PA9
	GPIOA->MODER |= (0x2UL << 18U);    // Set alternate function mode for PA9

	// Configure PA10 (RX) as Alternate Function 1, Push-Pull, No Pull-up/down
	GPIOA->AFRH &= ~(0xEUL << 8U);     // Clear alternate function bits for PA10
	GPIOA->AFRH |= (0x1UL << 8U);      // Set AF1 for PA10
	GPIOA->PUPDR &= ~(0x3UL << 20U);   // No pull-up, no pull-down for PA10
	GPIOA->OTYPER &= ~(0x1UL << 10U);  // Push-pull for PA10
	GPIOA->MODER &= ~(0x3UL << 20U);   // Clear mode bits for PA10
	GPIOA->MODER |= (0x2UL << 20U);    // Set alternate function mode for PA10

	// Set word length to 8 bits
	USART1->CR1 &= ~(0x1UL << 28U);    // Clear M1 bit
	USART1->CR1 &= ~(0x1UL << 12U);    // Clear M0 bit

	// Set baud rate (USART_BRR)
	USART1->BRR = 5000;                // Set baud rate register

	// Set 1 stop bit
	USART1->CR2 &= ~(0x3UL << 12U);    // Clear STOP bits

	// Enable USART1
	USART1->CR1 |= (0x1UL << 0U);      // Set UE bit

	// Enable transmitter
	USART1->CR1 |= (0x1UL << 3U);      // Set TE bit

	// Enable receiver
	USART1->CR1 |= (0x1UL << 2U);      // Set RE bit

	// Enable RXNE interrupt
	USART1->CR1 |= (0x1UL << 5U);      // Set RXNEIE bit
}

// Printf function for UART1
int _write(int file, char *ptr, int len) {
	int DataIdx;
	for (DataIdx = 0; DataIdx < len; DataIdx++) {
		while (!(USART1->ISR & (0x1UL << 7U))); // Wait until TXE is set
		USART1->TDR = *ptr++;                   // Send character
	}
	return len;
}
