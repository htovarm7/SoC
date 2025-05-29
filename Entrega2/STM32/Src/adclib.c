#include <stdint.h>
#include "main.h"
#include "systicklib.h"
#include "adclib.h"

// Initialize the ADC peripheral and configure GPIOA pin 0 as analog input
void USER_ADC_Init(void) {
    // Enable GPIOA and ADC clocks
    RCC->IOPENR |= (1 << 0);         // Enable GPIOA clock
    RCC->APBENR2 |= (1 << 20);       // Enable ADC clock

    // Set PA0 to analog mode, no pull-up/pull-down
    GPIOA->MODER |= (0x3 << (0 * 2));    // Analog mode for PA0
    GPIOA->PUPDR &= ~(0x3 << (0 * 2));   // No pull-up, no pull-down

    // Configure ADC clock mode: synchronous clock divided by 2
    ADC->CFGR2 &= ~(0x3 << 30);          // Clear CKMODE bits
    //ADC->CFGR2 |= (0x1 << 30);         // Uncomment to set CKMODE = 01 (PCLK/2)

    // Configure ADC common control register for clock
    ADC->CCR &= ~(0xE << 18);            // Clear clock bits
    ADC->CCR |= (0x1 << 18);             // Set clock to PCLK/2

    // Configure ADC: single conversion, right alignment, 12-bit resolution
    ADC->CFGR1 &= ~(0x1 << 13);          // Single conversion mode
    ADC->CFGR1 &= ~(0x1 << 5);           // Right data alignment
    ADC->CFGR1 &= ~(0x3 << 3);           // 12-bit resolution

    // Set sampling time to minimum
    ADC->SMPR &= ~(0x7 << 0);            // Shortest sampling time

    // Clear ADC ready and configuration bits
    ADC->ISR &= ~(0x1UL << 13U);         // Clear ADRDY
    ADC->CFGR1 &= ~(0x1UL << 21U) & ~(0x1UL << 2U); // Clear DMA and SCANDIR

    // Select channel 0 (PA0) for conversion
    ADC->CHSELR = (1 << 0);

    // Wait until ADC is ready
    while (!(ADC->ISR & (0x1UL << 13U)));

    // Enable internal voltage regulator
    ADC->CR |= (1 << 28);                // Enable ADVREGEN
    SysTick_Delay(1);                    // Wait >10 us for regulator startup

    // Calibrate ADC
    while (!USER_ADC_Calibration());

    // Enable ADC
    ADC->CR |= (1 << 0);                 // Set ADEN
    for (uint32_t i = 0; i < 1000 && !(ADC->ISR & (1 << 0)); i++) {
        SysTick_Delay(1);                // Wait up to 1ms for ADC ready
    }
    if (!(ADC->ISR & (1 << 0))) return;  // Abort if ADC not ready
}

// Calibrate the ADC and limit calibration factor if necessary
uint8_t USER_ADC_Calibration(void) {
    ADC->CR |= (1 << 31);                // Start calibration (ADCAL)
    while (ADC->CR & (1 << 31));         // Wait for calibration to finish

    // Limit calibration factor to maximum allowed value
    if (ADC->CALFACT > 0x7F) {
        ADC->CALFACT = 0x7F;
    }
    return 1;
}

// Start an ADC conversion and return the 12-bit result
uint16_t USER_ADC_Read(void) {
    ADC->CR |= (1 << 2);                 // Start conversion (ADSTART)
    while (!(ADC->ISR & (1 << 2)));      // Wait for end of conversion (EOC)
    if (ADC->ISR & (1 << 4)) {           // Check for overrun error
        ADC->ISR |= (1 << 4);            // Clear overrun flag
    }
    return (uint16_t)(ADC->DR);          // Return converted value
}
