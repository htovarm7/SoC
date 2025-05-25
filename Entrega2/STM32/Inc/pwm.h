#ifndef __PWM_H__
#define __PWM_H__

#include <stdint.h>

void PWM_Init(void);
void PWM_Set_Intensity_From_ADC(uint16_t adc_value);

#endif
