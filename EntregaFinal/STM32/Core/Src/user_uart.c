#include "main.h"
#include "user_uart.h"

// Initialize USART1 peripheral and configure GPIO pins for UART1
void USER_UART1_Init(void) {
  // Enable GPIOA clock
  RCC->IOPENR  |= (0x1UL << 0U);
  // Enable USART1 clock
  RCC->APBENR2 |= (0x1UL << 14U);

  // Configure PA9 and PA10 as Alternate Function for USART1 (AF1)
  GPIOA->AFR[1] &= ~((0xF << 4) | (0xF << 8)); // Clear alternate function bits for PA9 and PA10
  GPIOA->AFR[1] |=  (0x1 << 4) | (0x1 << 8);   // Set AF1 for PA9 and PA10
  GPIOA->PUPDR &= ~((0x3 << 18) | (0x3 << 20)); // No pull-up, pull-down for PA9 and PA10
  GPIOA->OTYPER &= ~((1 << 9) | (1 << 10));     // Set output type to push-pull for PA9 and PA10
  GPIOA->MODER &= ~((0x3 << 18) | (0x3 << 20)); // Clear mode bits for PA9 and PA10
  GPIOA->MODER |=  (0x2 << 18) | (0x2 << 20);   // Set PA9 and PA10 to alternate function mode

  // Configure USART1: 8 data bits, 1 stop bit, set baud rate
  USART1->CR1 &= ~((1 << 28) | (1 << 12)); // Set 8-bit word length
  USART1->CR2 &= ~(0x3 << 12);             // Set 1 stop bit
  USART1->BRR  = 5000;                     // Set baud rate for 9600 bps @ 48 MHz

  // Enable USART1, transmitter, receiver, and RXNE interrupt
  USART1->CR1 |= (1 << 0) | (1 << 2) | (1 << 3) | (1 << 5);

  // Enable USART1 interrupt in NVIC
  NVIC->ISER[0] = (1UL << 27);
}

// Initialize USART2 peripheral and configure GPIO pins for UART2
void USER_UART2_Init( void ){
  // Enable GPIOA clock
  RCC->IOPENR   |=  ( 0x1UL <<  0U );
  // Enable USART2 clock
  RCC->APBENR1  |=  ( 0x1UL << 17U );
  // Clear alternate function bits for PA2 (USART2_TX)
  GPIOA->AFR[0]   &= ~( 0xEUL <<  8U );
  // Set AF1 for PA2 (USART2_TX)
  GPIOA->AFR[0]   |=  ( 0x1UL <<  8U );
  // Clear pull-up/pull-down bits for PA2
  GPIOA->PUPDR  &= ~( 0x3UL <<  4U );
  // Set output type to push-pull for PA2
  GPIOA->OTYPER &= ~( 0x1UL <<  2U );
  // Clear mode bits for PA2
  GPIOA->MODER  &= ~( 0x1UL <<  4U );
  // Set PA2 as alternate function
  GPIOA->MODER  |=  ( 0x2UL <<  4U );
  // Clear alternate function bits for PA3 (USART2_RX)
  GPIOA->AFR[0]   &= ~( 0xEUL << 12U );
  // Set AF1 for PA3 (USART2_RX)
  GPIOA->AFR[0]   |=  ( 0x1UL << 12U );
  // Clear pull-up/pull-down bits for PA3
  GPIOA->PUPDR  &= ~( 0x3UL <<  6U );
  // Set output type to push-pull for PA3
  GPIOA->OTYPER &= ~( 0x1UL <<  3U );
  // Clear mode bits for PA3
  GPIOA->MODER  &= ~( 0x1UL <<  6U );
  // Set PA3 as alternate function
  GPIOA->MODER  |=  ( 0x2UL <<  6U );
  // Set 8-bit word length for USART2
  USART2->CR1   &= ~( 0x1UL << 28U );
  USART2->CR1   &= ~( 0x1UL << 12U );
  // Set baud rate for USART2 (115200 bps @ 48 MHz)
  USART2->BRR   =   ( 48000000 / 115200 );
  // Set 1 stop bit for USART2
  USART2->CR2   &= ~( 0x3UL << 12U );
  // Enable USART2
  USART2->CR1   |=  ( 0x1UL <<  0U );
  // Enable transmitter for USART2
  USART2->CR1   |=  ( 0x1UL <<  3U );
  // Enable receiver for USART2
  USART2->CR1   |=  ( 0x1UL <<  2U );
}

// Custom implementation of the _write function for printf redirection to USART1
int _write(int file, char *ptr, int len){
  int DataIdx;
  // Loop through each character to send
  for(DataIdx=0; DataIdx<len; DataIdx++){
    // Wait until transmit data register is empty
    while(!( USART1->ISR & (0x1UL << 7U)));
    // Send character
    USART1->TDR = *ptr++;
  }
  // Return number of bytes written
  return len;
}

// Send a single 8-bit data via USART1
static void USER_UART1_Send_8bit( uint8_t Data ){
  // Wait until transmit data register is empty
  while(!( USART1->ISR & ( 0x1UL <<  7U)));
  // Send data
  USART1->TDR = Data;
}

// Transmit an array of bytes via USART1
void USER_UART1_Transmit( uint8_t *pData, uint16_t size ){
  // Loop through each byte and send
  for( int i = 0; i < size; i++ ){
    USER_UART1_Send_8bit( *pData++ );
  }
}
