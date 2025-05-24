#ifndef INC_LCD_H_
#define INC_LCD_H_

// Set RS_LCD pin (PB9) high
#define LCD_RS_PIN_HIGH       ( 0x1UL <<  9U )
// Set RW_LCD pin (PB10) high
#define LCD_RW_PIN_HIGH       ( 0x1UL << 10U )
// Set EN_LCD pin (PB11) high
#define LCD_EN_PIN_HIGH       ( 0x1UL << 11U )

// Reset RS_LCD pin (PB9) low
#define LCD_RS_PIN_LOW        ( 0x1UL << 25U )
// Reset RW_LCD pin (PB10) low
#define LCD_RW_PIN_LOW        ( 0x1UL << 26U )
// Reset EN_LCD pin (PB11) low
#define LCD_EN_PIN_LOW        ( 0x1UL << 27U )

// Set DATA4_LCD pin (PB12) high
#define LCD_D4_PIN_HIGH       ( 0x1UL << 12U )
// Set DATA5_LCD pin (PB13) high
#define LCD_D5_PIN_HIGH       ( 0x1UL << 13U )
// Set DATA6_LCD pin (PB14) high
#define LCD_D6_PIN_HIGH       ( 0x1UL << 14U )
// Set DATA7_LCD pin (PB15) high
#define LCD_D7_PIN_HIGH       ( 0x1UL << 15U )

// Reset DATA4_LCD pin (PB12) low
#define LCD_D4_PIN_LOW        ( 0x1UL << 28U )
// Reset DATA5_LCD pin (PB13) low
#define LCD_D5_PIN_LOW        ( 0x1UL << 29U )
// Reset DATA6_LCD pin (PB14) low
#define LCD_D6_PIN_LOW        ( 0x1UL << 30U )
// Reset DATA7_LCD pin (PB15) low
#define LCD_D7_PIN_LOW        ( 0x1UL << 31U )

// LCD command: Clear display
#define LCD_Clear( )            LCD_Write_Cmd( 0x01U )
// LCD command: Display ON
#define LCD_Display_ON( )       LCD_Write_Cmd( 0x0EU )
// LCD command: Display OFF
#define LCD_Display_OFF( )      LCD_Write_Cmd( 0x08U )
// LCD command: Cursor Home
#define LCD_Cursor_Home( )      LCD_Write_Cmd( 0x02U )
// LCD command: Cursor Blink
#define LCD_Cursor_Blink( )     LCD_Write_Cmd( 0x0FU )
// LCD command: Cursor ON
#define LCD_Cursor_ON( )        LCD_Write_Cmd( 0x0EU )
// LCD command: Cursor OFF
#define LCD_Cursor_OFF( )       LCD_Write_Cmd( 0x0CU )
// LCD command: Move cursor left
#define LCD_Cursor_Left( )      LCD_Write_Cmd( 0x10U )
// LCD command: Move cursor right
#define LCD_Cursor_Right( )     LCD_Write_Cmd( 0x14U )
// LCD command: Shift display left
#define LCD_Cursor_SLeft( )     LCD_Write_Cmd( 0x18U )
// LCD command: Shift display right
#define LCD_Cursor_SRight( )    LCD_Write_Cmd( 0x1CU )

// Function to output 4 bits of data to LCD
void LCD_Data_Out4(uint8_t val);
// Function to write a byte to LCD
void LCD_Write_Byte(uint8_t val);
// Function to write a command to LCD
void LCD_Write_Cmd(uint8_t val);
// Function to write a character to LCD
void LCD_Put_Char(uint8_t c);
// Function to initialize the LCD
void LCD_Init(void);
// Function to set the cursor position
void LCD_Set_Cursor(uint8_t line, uint8_t column);
// Function to write a string to LCD
void LCD_Put_Str(char * str);
// Function to write a number to LCD
void LCD_Put_Num(int16_t num);
// Function to check if LCD is busy
char LCD_Busy(void);
// Function to generate enable pulse for LCD
void LCD_Pulse_EN(void);
// Function to display a bar graph on LCD
void LCD_BarGraphic(int16_t value, int16_t size);
// Function to display a bar graph at specific position
void LCD_BarGraphicXY(int16_t pos_x, int16_t pos_y, int16_t value);

#endif /* INC_LCD_H_ */
