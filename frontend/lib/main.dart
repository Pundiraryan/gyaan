import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/daily_insights_tab.dart';
import 'screens/learn_anything_tab.dart';

void main() {
  runApp(const ProviderScope(child: GyaanApp()));
}

class GyaanApp extends StatelessWidget {
  const GyaanApp({super.key});

  @override
  Widget build(BuildContext context) {
    final darkTheme = ThemeData.dark(useMaterial3: true).copyWith(
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFFFF7A1A),
        brightness: Brightness.dark,
        primary: const Color(0xFFFF7A1A),
        secondary: const Color(0xFF5BE38D),
        tertiary: const Color(0xFF8B5CF6),
      ),
      scaffoldBackgroundColor: const Color(0xFF07111F),
      cardTheme: const CardThemeData(
        elevation: 3,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(20)),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF0F172A),
        foregroundColor: Colors.white,
      ),
      navigationBarTheme: const NavigationBarThemeData(
        backgroundColor: Color(0xFF0F172A),
        indicatorColor: Color(0x33FF7A1A),
      ),
    );

    return MaterialApp(
      title: 'GYAAN',
      theme: darkTheme,
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = [const DailyInsightsTab(), const LearnAnythingTab()];
    return Scaffold(
      appBar: AppBar(title: const Text('GYAAN')),
      body: pages[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (value) => setState(() => _currentIndex = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.lightbulb), label: 'Daily'),
          NavigationDestination(icon: Icon(Icons.school), label: 'Learn'),
        ],
      ),
    );
  }
}
