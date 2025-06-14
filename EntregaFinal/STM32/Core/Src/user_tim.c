#include <stdint.h>
#include "main.h"
#include "user_tim.h"

// Initializes TIM3 for PWM output on PB4 and PB5 (CH1 and CH2)
void USER_TIM3_PWM_Init(void) {
	// Enable GPIOB and TIM3 clocks
	RCC->IOPENR  |= (1UL << 1U);
	RCC->APBENR1 |= (1UL << 1U);

	// Configure PB4 (TIM3_CH1) as alternate function (AF1)
	GPIOB->AFR[0] &= ~(0xFUL << 16U);
	GPIOB->AFR[0] |=  (0x1UL << 16U);
	GPIOB->PUPDR  &= ~(0x3UL << 8U);
	GPIOB->OTYPER &= ~(0x1UL << 4U);
	GPIOB->MODER  &= ~(0x3UL << 8U);
	GPIOB->MODER  |=  (0x2UL << 8U);

	// Configure PB5 (TIM3_CH2) as alternate function (AF1)
	GPIOB->AFR[0] &= ~(0xFUL << 20U);
	GPIOB->AFR[0] |=  (0x1UL << 20U);
	GPIOB->PUPDR  &= ~(0x3UL << 10U);
	GPIOB->OTYPER &= ~(0x1UL << 5U);
	GPIOB->MODER  &= ~(0x3UL << 10U);
	GPIOB->MODER  |=  (0x2UL << 10U);

	// Internal clock source
	TIM3->SMCR &= ~(0x1UL << 16U) & ~(0x7UL << 0U);

	// Edge-aligned, upcounter, UEV enabled, ARR buffered
	TIM3->CR1 &= ~(0x3UL << 5U) & ~(0x1UL << 4U) & ~(0x1UL << 2U) & ~(0x1UL << 1U);
	TIM3->CR1 |=  (0x1UL << 7U);

	// Prescaler and period for 1 kHz PWM (assuming 48 MHz clock)
	TIM3->PSC  = 0U;
	TIM3->ARR  = 47999U;

	// Set initial duty cycle to 0% for all channels
	TIM3->CCR1 = USER_Duty_Cycle(0);
	TIM3->CCR2 = USER_Duty_Cycle(0);
	TIM3->CCR3 = USER_Duty_Cycle(0);
	TIM3->CCR4 = USER_Duty_Cycle(0);

	// Configure PWM mode 1 for CH1 and CH2, preload enable
	TIM3->CCMR1 &= ~(0xFFUL << 0U);
	TIM3->CCMR1 |=  (0x6UL << 4U) | (0x1UL << 3U); // CH1
	TIM3->CCMR1 |=  (0x6UL << 12U) | (0x1UL << 11U); // CH2

	// Enable output and set polarity for all channels
	TIM3->CCER = 0;
	TIM3->CCER |= (1UL << 0U);   // CH1 enable
	TIM3->CCER |= (1UL << 4U);   // CH2 enable
	TIM3->CCER |= (1UL << 8U);   // CH3 enable
	TIM3->CCER |= (1UL << 12U);  // CH4 enable

	// Generate update event to load registers
	TIM3->EGR |= (1UL << 0U);

	// Enable TIM3 counter
	TIM3->CR1 |= (1UL << 0U);
}

// Initializes TIM14 for microsecond delay
void USER_TIM14_Init(void) {
	RCC->APBENR2 |= (1UL << 15U);
	TIM14->SMCR &= ~(0x1UL << 16U) & ~(0x7UL << 0U);
	TIM14->CR1  &= ~(0x1UL << 7U) & ~(0x3UL << 5U) & ~(0x1UL << 4U) & ~(0x1UL << 1U);
}

// Microsecond delay using TIM14
void USER_TIM14_Delay(uint16_t us) {
	TIM14->CR1 &= ~(1UL << 0);         // Disable timer
	TIM14->PSC = 47;                   // 1 MHz tick (assuming 48 MHz clock)
	TIM14->ARR = us;                   // Set auto-reload for desired delay
	TIM14->EGR |= (1UL << 0);          // Update registers
	TIM14->SR  &= ~(1UL << 0);         // Clear update flag
	TIM14->CR1 |= (1UL << 0);          // Enable timer
	while (!(TIM14->SR & (1UL << 0))); // Wait for overflow
	TIM14->CR1 &= ~(1UL << 0);         // Disable timer
	TIM14->SR  &= ~(1UL << 0);         // Clear flag
}

// Initializes TIM17 as a general-purpose timer
void USER_TIM17_Init_Timer(void) {
	RCC->APBENR2 |= (1UL << 18U);      // Enable TIM17 clock
	TIM17->CR1   &= ~(1UL << 7U) & ~(1UL << 1U);
	TIM17->PSC    = 1499U;             // Prescaler
	TIM17->ARR    = 65535U;            // Max count
	TIM17->SR    &= ~(1UL << 0U);      // Clear overflow flag
	TIM17->CR1   |= (1UL << 0U);       // Enable timer
}

// Update PWM duty cycle for selected channel (1-4)
void update_cycle(uint8_t duty, uint8_t pin) {
	switch (pin) {
		case 1: TIM3->CCR1 = USER_Duty_Cycle(duty); break;
		case 2: TIM3->CCR2 = USER_Duty_Cycle(duty); break;
		case 3: TIM3->CCR3 = USER_Duty_Cycle(duty); break;
		case 4: TIM3->CCR4 = USER_Duty_Cycle(duty); break;
		default: break;
	}
}

// Calculate CCR value for given duty cycle (0-100%)
uint16_t USER_Duty_Cycle(uint8_t duty) {
	if (duty <= 100)
		return (uint16_t)(((float)duty / 100.0f) * (TIM3->ARR + 1));
	else
		return 0;
}
