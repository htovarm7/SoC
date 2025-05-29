#ifndef USER_TIM_H_
#define USER_TIM_H_

typedef struct
{
	volatile uint32_t CR1;
	volatile uint32_t CR2;
	volatile uint32_t SMCR;
	volatile uint32_t DIER;
	volatile uint32_t SR;
	volatile uint32_t EGR;
	volatile uint32_t CCMR1;
	volatile uint32_t CCMR2;
	volatile uint32_t CCER;
	volatile uint32_t CNT;
	volatile uint32_t PSC;
	volatile uint32_t ARR;
	volatile uint32_t RESERVED1;
	volatile uint32_t CCR1;
	volatile uint32_t CCR2;
	volatile uint32_t CCR3;
	volatile uint32_t CCR4;
	volatile uint32_t RESERVED2;
	volatile uint32_t DCR;
	volatile uint32_t DMAR;
	volatile uint32_t RESERVED3[5];
	volatile uint32_t AF1;
	volatile uint32_t RESERVED4;
	volatile uint32_t TISEL;
} TIM_TypeDef;

#define TIM3_BASE	0x40000400UL
#define TIM3    	(( TIM_TypeDef * )TIM3_BASE )

void USER_TIM3_PWM_Init( void );
void update_cycle(uint8_t duty);
uint16_t USER_Duty_Cycle( uint8_t duty );

#endif /* USER_TIM_H_ */