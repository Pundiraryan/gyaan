// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:gyaan/main.dart';

void main() {
  testWidgets('App launches with the daily insights screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: GyaanApp()));

    expect(find.text('GYAAN'), findsWidgets);
    expect(find.text('Daily'), findsOneWidget);
  });
}
