import 'package:flutter/material.dart';
import 'package:storypals_mobile/widgets/insight_card.dart';
import 'package:storypals_mobile/widgets/progress_chart.dart';
import 'package:storypals_mobile/widgets/activity_list.dart';
import 'package:storypals_mobile/theme/app_theme.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text(
          'Dashboard',
          style: TextStyle(
            fontSize: 24.0,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              // Handle notifications
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Section
            Container(
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor,
                borderRadius: BorderRadius.circular(16.0),
              ),
              child: Row(
                children: [
                  const CircleAvatar(
                    radius: 30.0,
                    backgroundImage: AssetImage('assets/images/child_avatar.png'),
                  ),
                  const SizedBox(width: 16.0),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Welcome back!',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18.0,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4.0),
                        Text(
                          'Let\'s continue learning together',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.8),
                            fontSize: 14.0,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24.0),

            // Insights Section
            const Text(
              'Today\'s Insights',
              style: TextStyle(
                fontSize: 20.0,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16.0),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              mainAxisSpacing: 16.0,
              crossAxisSpacing: 16.0,
              childAspectRatio: 1.5,
              children: [
                InsightCard(
                  title: 'Words Learned',
                  value: '12',
                  icon: Icons.text_fields,
                  color: Colors.blue,
                ),
                InsightCard(
                  title: 'Stories Read',
                  value: '3',
                  icon: Icons.book,
                  color: Colors.green,
                ),
                InsightCard(
                  title: 'Time Spent',
                  value: '45m',
                  icon: Icons.timer,
                  color: Colors.orange,
                ),
                InsightCard(
                  title: 'Progress',
                  value: '85%',
                  icon: Icons.trending_up,
                  color: Colors.purple,
                ),
              ],
            ),
            const SizedBox(height: 24.0),

            // Progress Chart
            const ProgressChart(
              title: 'Weekly Progress',
              data: [0.3, 0.5, 0.7, 0.6, 0.8, 0.9, 0.85],
            ),
            const SizedBox(height: 24.0),

            // Recent Activities
            ActivityList(
              title: 'Recent Activities',
              activities: [
                {
                  'type': 'story',
                  'title': 'The Space Adventure',
                  'description': 'Completed reading with 90% comprehension',
                  'timestamp': DateTime.now().subtract(const Duration(hours: 2)),
                },
                {
                  'type': 'vocabulary',
                  'title': 'New Words',
                  'description': 'Learned 5 new words about space',
                  'timestamp': DateTime.now().subtract(const Duration(hours: 3)),
                },
                {
                  'type': 'quiz',
                  'title': 'Space Quiz',
                  'description': 'Scored 8/10 in the space knowledge quiz',
                  'timestamp': DateTime.now().subtract(const Duration(hours: 4)),
                },
              ],
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        selectedItemColor: AppTheme.primaryColor,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.book),
            label: 'Stories',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
} 