#include <stdint.h>
#include "main.h"
#include "custom_timer.h"
#include "custom_uart.h"
#include "lcd_driver.h"
#include "systick_delay.h"
#include "adc_reader.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_BUFFER 8

char str_temp[MAX_BUFFER];
char str_speed[MAX_BUFFER];
char str_rpm[MAX_BUFFER];
char str_gear[MAX_BUFFER];
int current_speed = 0;
int char_count = 0;

uint8_t btn_flag = 0;
uint16_t pot_value;

void USART1_IRQHandler(void)
{
	if ((USART1->ISR & (1U << 5)))
	{
		char incoming = USART1->RDR;
		if (incoming == 'V')
		{
			current_speed = atoi(str_temp);
			memcpy(str_speed, str_temp, sizeof(str_temp));
			memset(str_temp, 0, sizeof(str_temp));
			char_count = 0;
		}
		else if (incoming == 'S')
		{
			memcpy(str_rpm, str_temp, sizeof(str_temp));
			memset(str_temp, 0, sizeof(str_temp));
			char_count = 0;
		}
		else if (incoming == 'E')
		{
			memcpy(str_gear, str_temp, sizeof(str_temp));
			memset(str_temp, 0, sizeof(str_temp));
			char_count = 0;
		}
		else
		{
			if (char_count < MAX_BUFFER - 1)
			{
				str_temp[char_count++] = incoming;
			}
			else
			{
				memset(str_temp, 0, sizeof(str_temp));
				char_count = 0;
			}
		}
	}
}

int main(void)
{
	SystemClock_Config();
	Timer3_PWM_Config();
	Configure_SysTick();
	UART1_Configure();
	LED_Init();
	LCD_Init();
	ADC_Setup();
	EXTI1_Setup();

	LCD_Clear();

	while (1)
	{
		pot_value = ADC_Read_Value();

		btn_flag = (GPIOA->IDR & (1U << 7)) ? 1 : 0;

		if (current_speed > 100)
		{
			current_speed = 100;
		}

		LCD_Set_Cursor(1, 1);
		LCD_Put_Str("Spd:      G:");
		LCD_Set_Cursor(1, 6);
		LCD_Put_Str(str_speed);
		LCD_Set_Cursor(1, 14);
		LCD_Put_Str(str_gear);
		LCD_Set_Cursor(2, 1);
		LCD_Put_Str("RPM:     ");
		LCD_Set_Cursor(2, 6);
		LCD_Put_Str(str_rpm);
		update_motor_speed(current_speed);

		printf("{adc: %u, button: %u}\n", pot_value, btn_flag);
		Delay_ms(100);
	}
}

void LED_Init(void)
{
	RCC->IOPENR |= (1U << 0);	// Enable clock for GPIOA

	GPIOA->BSRR = (1U << 21);	// Reset PA5
	GPIOA->PUPDR &= ~(3U << 10);
	GPIOA->OTYPER &= ~(1U << 5);
	GPIOA->MODER &= ~(3U << 10);
	GPIOA->MODER |= (1U << 10);	// Set PA5 as output

	GPIOA->MODER &= ~(3U << 14);	// PA7 as input
	GPIOA->PUPDR &= ~(3U << 14);
	GPIOA->PUPDR |= (2U << 14);		// Pull-down
}

void SystemClock_Config(void)
{
	RCC->CR &= ~(7U << 11);
	while (!(RCC->CR & (1U << 10)));

	RCC->CFGR &= ~(7U << 0);
	RCC->CFGR &= ~(1U << 11);

	FLASH->ACR &= ~(7U);
	FLASH->ACR |= (1U);
	while ((FLASH->ACR & 7U) != 1U);
}
