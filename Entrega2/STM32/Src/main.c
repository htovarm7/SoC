#include <stdint.h>
#include "main.h"
#include "user_tim.h"
#include "user_uart.h"
#include "lcd.h"
#include "systicklib.h"
#include "adclib.h"

int main(void)
{
	// Initialize system clock and peripherals
	USER_RCC_Init();
	USER_SysTick_Init();
	USER_UART1_Init();
	USER_GPIO_Init();
	LCD_Init();
	USER_ADC_Init();

	uint8_t button_status = 0;
	uint16_t val = 0;

	LCD_Clear();

	for(;;){
			LCD_Clear();

			// Read ADC value
			val = USER_ADC_Read();

			// Read button status from UART (not used below)
			button_status = USER_UART1_Receive_8bit();

			// Check if button (PA9) is pressed
			if(GPIOA->IDR & (0x1UL << 9U)){
					button_status = 1; 
			}
			else{
					button_status = 0;
			}

			// Display ADC value on LCD
			LCD_Set_Cursor(1, 1);
			LCD_Put_Str("ADC: ");
			LCD_Put_Num(val);

			// Display button status on LCD
			LCD_Set_Cursor(2, 1);
			LCD_Put_Str("Button: ");
			LCD_Put_Num(button_status);

			// Delay for 100 ms
			SysTick_Delay(100);

			// Toggle LED on PA5
			GPIOA->ODR ^= (0x1UL << 5U); 
	}
}

// Configure system clock and enable GPIOA peripheral
void USER_RCC_Init(void){
		// Enable GPIOA clock
		RCC->IOPENR = RCC->IOPENR | (0x1UL << 0U);

		// Set Flash latency for 48 MHz operation
		FLASH->ACR &= ~(0x6UL << 0U); // Clear latency bits
		FLASH->ACR |=  (0x1UL << 0U); // Set 2 HCLK cycles latency
		while((FLASH->ACR & (0x7UL << 0U)) != 0x001UL); // Wait for latency to be set

		// Set HSISYS division factor to 1
		RCC->CR &= ~(0x7UL << 11U);
		while(!(RCC->CR & (0x1UL << 10U))); // Wait for HSISYS ready

		// Select HSISYS as SYSCLK source and set HCLK division factor to 1
		RCC->CFGR &= ~(0x7UL << 0U);
		RCC->CFGR &= ~(0x1UL << 11U);
}

// Configure GPIOA pins: PA5 as output (LED), PA9 as input with pull-down (button)
void USER_GPIO_Init(void){
		// Set PA5 (LED) as output, push-pull, no pull-up/pull-down, and turn off LED
		GPIOA->BSRR   = 0x1UL << 21U; // Reset PA5 (turn off LED)
		GPIOA->PUPDR  = GPIOA->PUPDR  & ~(0x3UL << 10U); // No pull-up/pull-down for PA5
		GPIOA->OTYPER = GPIOA->OTYPER & ~(0x1UL << 5U);  // Push-pull output for PA5
		GPIOA->MODER  = GPIOA->MODER  & ~(0x2UL << 10U); // Clear mode bits for PA5
		GPIOA->MODER  = GPIOA->MODER  |  (0x1UL << 10U); // Set PA5 as output

		// Set PA9 (button) as input with pull-down resistor
		GPIOA->MODER &= ~(0x3UL << 18U); // Set PA9 as input
		GPIOA->PUPDR &= ~(0x1UL << 18U); // Clear pull-up bit for PA9
		GPIOA->PUPDR |=  (0x2UL << 18U); // Enable pull-down for PA9
}
