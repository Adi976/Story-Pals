import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:storypals_mobile/screens/auth_screen.dart';
import 'package:storypals_mobile/screens/chat_screen.dart';
import 'dart:math';

class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.2),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFB5A8E0),
              Color(0xFFD5A8F0),
            ],
          ),
        ),
        child: Stack(
          children: [
            // Animated background elements
            Positioned.fill(
              child: CustomPaint(
                painter: BackgroundPainter(),
              ),
            ),
            
            // Content
            SafeArea(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Navbar
                    _Navbar(),
                    
                    // Main Content
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const SizedBox(height: 40),
                          
                          // Logo and Title
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Column(
                                children: [
                                  SvgPicture.asset(
                                    'assets/icons/storypals_logo.svg',
                                    height: 80,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'StoryPals',
                                    style: GoogleFonts.poppins(
                                      fontSize: 48,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                      shadows: [
                                        Shadow(
                                          color: Colors.black.withOpacity(0.2),
                                          offset: const Offset(0, 3),
                                          blurRadius: 10,
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Hero Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Column(
                                children: [
                                  Text(
                                    'Magical Friends for Young Storytellers',
                                    style: GoogleFonts.poppins(
                                      fontSize: 32,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                      shadows: [
                                        Shadow(
                                          color: Colors.black.withOpacity(0.2),
                                          offset: const Offset(0, 2),
                                          blurRadius: 4,
                                        ),
                                      ],
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    'StoryPals brings storytelling to life with interactive AI companions who listen, respond, and create magical adventures alongside your child. Safe, educational, and endlessly imaginative!',
                                    style: GoogleFonts.poppins(
                                      fontSize: 16,
                                      color: Colors.white,
                                      height: 1.6,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Characters Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: GridView.count(
                                shrinkWrap: true,
                                physics: const NeverScrollableScrollPhysics(),
                                crossAxisCount: 2,
                                mainAxisSpacing: 20,
                                crossAxisSpacing: 20,
                                children: [
                                  _CharacterCard(
                                    name: 'Luna',
                                    description: 'The friendly star fairy who knows all about space and dreams',
                                    imagePath: 'assets/images/luna.png',
                                  ),
                                  _CharacterCard(
                                    name: 'Captain Leo',
                                    description: 'A brave explorer with tales of adventure from distant lands',
                                    imagePath: 'assets/images/captain_leo.png',
                                  ),
                                  _CharacterCard(
                                    name: 'Whiskers',
                                    description: 'The curious cat who loves solving mysteries and riddles',
                                    imagePath: 'assets/images/whiskers.png',
                                  ),
                                  _CharacterCard(
                                    name: 'Melody',
                                    description: 'A musical woodland sprite who teaches through songs and rhymes',
                                    imagePath: 'assets/images/melody.png',
                                  ),
                                ],
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Expanded Features Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Column(
                                children: [
                                  Text(
                                    'Magical Features for Young Minds',
                                    style: GoogleFonts.poppins(
                                      fontSize: 28,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    'StoryPals combines cutting-edge AI with child development expertise to create safe, engaging, and educational experiences.',
                                    style: GoogleFonts.poppins(
                                      fontSize: 16,
                                      color: Colors.white,
                                      height: 1.6,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 30),
                                  GridView.count(
                                    shrinkWrap: true,
                                    physics: const NeverScrollableScrollPhysics(),
                                    crossAxisCount: 2,
                                    mainAxisSpacing: 20,
                                    crossAxisSpacing: 20,
                                    children: [
                                      _FeatureCard(
                                        icon: Icons.auto_stories,
                                        title: 'Interactive Storytelling',
                                        description: 'Children can co-create stories with their StoryPal, developing creativity and narrative skills while having fun. Each story can be saved and revisited!',
                                      ),
                                      _FeatureCard(
                                        icon: Icons.shield,
                                        title: 'Child-Safe Environment',
                                        description: 'StoryPals is designed with safety first. All content is age-appropriate and interactions are monitored with advanced safety protocols.',
                                      ),
                                      _FeatureCard(
                                        icon: Icons.school,
                                        title: 'Educational Content',
                                        description: 'Each character specializes in different educational areas, from science and nature to language arts, making learning an adventure!',
                                      ),
                                      _FeatureCard(
                                        icon: Icons.brush,
                                        title: 'Creative Companion',
                                        description: 'StoryPals respond to children\'s ideas, ask thoughtful questions, and encourage imagination in a supportive, engaging way.',
                                      ),
                                      _FeatureCard(
                                        icon: Icons.person,
                                        title: 'Personalized Experience',
                                        description: 'StoryPals remember preferences, past stories, and adapt to each child\'s interests and learning pace.',
                                      ),
                                      _FeatureCard(
                                        icon: Icons.psychology,
                                        title: 'Emotional Intelligence',
                                        description: 'StoryPals help children explore emotions through stories, building empathy and emotional vocabulary.',
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Chat Demo Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(20),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.1),
                                      blurRadius: 20,
                                      offset: const Offset(0, 10),
                                    ),
                                  ],
                                ),
                                padding: const EdgeInsets.all(20),
                                child: Column(
                                  children: [
                                    Text(
                                      'Meet Your StoryPal',
                                      style: GoogleFonts.poppins(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: const Color(0xFF7B5EA7),
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(height: 10),
                                    Text(
                                      'Try a conversation with one of our magical friends and see the StoryPals experience!',
                                      style: GoogleFonts.poppins(
                                        fontSize: 16,
                                        color: const Color(0xFF483C67),
                                        height: 1.6,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(height: 20),
                                    _ChatDemo(),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Testimonials Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Column(
                                children: [
                                  Text(
                                    'What Families Are Saying',
                                    style: GoogleFonts.poppins(
                                      fontSize: 28,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    'Join thousands of happy families who\'ve discovered the magic of StoryPals',
                                    style: GoogleFonts.poppins(
                                      fontSize: 16,
                                      color: Colors.white,
                                      height: 1.6,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 30),
                                  SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Row(
                                      children: [
                                        _TestimonialCard(
                                          name: 'Sarah M.',
                                          role: 'Parent of Alex, 6',
                                          text: 'StoryPals has completely transformed our bedtime routine. My son Alex used to resist going to bed, but now he can\'t wait to continue his adventure with Captain Leo.',
                                        ),
                                        _TestimonialCard(
                                          name: 'David T.',
                                          role: 'Father of Lily, 7',
                                          text: 'As a busy parent, I was looking for something both entertaining and educational. StoryPals exceeded my expectations.',
                                        ),
                                        _TestimonialCard(
                                          name: 'Maya J.',
                                          role: 'Mother of Twins, 5',
                                          text: 'My twins have very different interests, but StoryPals adapts to both of them perfectly. The personalization is impressive!',
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                          
                          // Parent Section
                          FadeTransition(
                            opacity: _fadeAnimation,
                            child: SlideTransition(
                              position: _slideAnimation,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(20),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.1),
                                      blurRadius: 20,
                                      offset: const Offset(0, 10),
                                    ),
                                  ],
                                ),
                                padding: const EdgeInsets.all(20),
                                child: Column(
                                  children: [
                                    Text(
                                      'For Parents: Safety & Learning',
                                      style: GoogleFonts.poppins(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: const Color(0xFF7B5EA7),
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(height: 20),
                                    Text(
                                      'StoryPals was designed with parents in mind. Our comprehensive parent dashboard gives you complete oversight and control of your child\'s experience while providing insights into their learning journey.',
                                      style: GoogleFonts.poppins(
                                        fontSize: 16,
                                        color: const Color(0xFF483C67),
                                        height: 1.6,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    const SizedBox(height: 30),
                                    Column(
                                      children: [
                                        _ParentFeature(
                                          icon: Icons.check_circle,
                                          text: 'Content control and activity monitoring',
                                        ),
                                        _ParentFeature(
                                          icon: Icons.check_circle,
                                          text: 'Learning progress reports and insights',
                                        ),
                                        _ParentFeature(
                                          icon: Icons.check_circle,
                                          text: 'Time limits and usage schedules',
                                        ),
                                        _ParentFeature(
                                          icon: Icons.check_circle,
                                          text: 'Save and share your child\'s stories',
                                        ),
                                        _ParentFeature(
                                          icon: Icons.check_circle,
                                          text: 'Educational focus customization',
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          
                          const SizedBox(height: 40),
                        ],
                      ),
                    ),
                    
                    // Footer
                    _Footer(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Navbar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              SvgPicture.asset(
                'assets/icons/storypals_logo.svg',
                height: 40,
              ),
              const SizedBox(width: 10),
              Text(
                'StoryPals',
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF7B5EA7),
                ),
              ),
            ],
          ),
          Row(
            children: [
              TextButton(
                onPressed: () {},
                child: Text(
                  'Home',
                  style: GoogleFonts.poppins(
                    color: const Color(0xFF483C67),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {},
                child: Text(
                  'About',
                  style: GoogleFonts.poppins(
                    color: const Color(0xFF483C67),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {},
                child: Text(
                  'Features',
                  style: GoogleFonts.poppins(
                    color: const Color(0xFF483C67),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              TextButton(
                onPressed: () {},
                child: Text(
                  'For Parents',
                  style: GoogleFonts.poppins(
                    color: const Color(0xFF483C67),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const AuthScreen(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF7B5EA7),
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(25),
                  ),
                ),
                child: Text(
                  'Parent Login',
                  style: GoogleFonts.poppins(
                    color: Colors.white,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ChatDemo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF9F5FF),
        borderRadius: BorderRadius.circular(15),
      ),
      padding: const EdgeInsets.all(15),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: const Color(0xFFF0C3E9),
                    width: 2,
                  ),
                  image: const DecorationImage(
                    image: AssetImage('assets/images/luna.png'),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'Luna the Star Fairy',
                style: GoogleFonts.poppins(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF7B5EA7),
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFE9DFFF),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              'Hello there, young storyteller! I\'m Luna, the Star Fairy. What magical adventure shall we create today?',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: const Color(0xFF483C67),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF7B5EA7),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              'Can we go on a trip to the moon?',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFE9DFFF),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              'What a wonderful idea! I know all about the moon! Did you know that the moon is Earth\'s only natural satellite? Let\'s pack our special space backpacks. What should we bring on our moon adventure?',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: const Color(0xFF483C67),
              ),
            ),
          ),
          const SizedBox(height: 15),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(25),
              border: Border.all(
                color: const Color(0xFFE9DFFF),
              ),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Type your message...',
                      hintStyle: GoogleFonts.poppins(
                        color: const Color(0xFF483C67).withOpacity(0.5),
                      ),
                      border: InputBorder.none,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () {},
                  icon: const Icon(
                    Icons.send,
                    color: Color(0xFF7B5EA7),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TestimonialCard extends StatelessWidget {
  final String name;
  final String role;
  final String text;

  const _TestimonialCard({
    required this.name,
    required this.role,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 350,
      margin: const EdgeInsets.only(right: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: const Color(0xFFF0C3E9),
                    width: 2,
                  ),
                  image: const DecorationImage(
                    image: AssetImage('assets/images/placeholder_avatar.png'),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(width: 15),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF7B5EA7),
                    ),
                  ),
                  Text(
                    role,
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      color: const Color(0xFF483C67),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 15),
          Text(
            text,
            style: GoogleFonts.poppins(
              fontSize: 14,
              color: const Color(0xFF483C67),
              height: 1.6,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ),
    );
  }
}

class _ParentFeature extends StatelessWidget {
  final IconData icon;
  final String text;

  const _ParentFeature({
    required this.icon,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(
            icon,
            color: const Color(0xFFFF9E6D),
            size: 20,
          ),
          const SizedBox(width: 10),
          Text(
            text,
            style: GoogleFonts.poppins(
              fontSize: 14,
              color: const Color(0xFF483C67),
            ),
          ),
        ],
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF483C67),
      padding: const EdgeInsets.all(40),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _FooterColumn(
                title: 'About',
                items: [
                  'Home',
                  'About Us',
                  'Our Characters',
                  'For Parents',
                  'Safety & Privacy',
                  'Subscription Plans',
                ],
              ),
              _FooterColumn(
                title: 'Contact',
                items: [
                  'hello@storypals.com',
                  '+1 (555) 123-4567',
                  '123 Imagination Lane, Storyville, ST 12345',
                ],
              ),
              _FooterColumn(
                title: 'Follow Us',
                items: [
                  'Facebook',
                  'Twitter',
                  'Instagram',
                  'YouTube',
                ],
              ),
            ],
          ),
          const SizedBox(height: 40),
          const Divider(
            color: Colors.white24,
          ),
          const SizedBox(height: 20),
          Text(
            '© 2024 StoryPals. All rights reserved.',
            style: GoogleFonts.poppins(
              color: Colors.white,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}

class _FooterColumn extends StatelessWidget {
  final String title;
  final List<String> items;

  const _FooterColumn({
    required this.title,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 15),
        ...items.map((item) => Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Text(
            item,
            style: GoogleFonts.poppins(
              color: Colors.white.withOpacity(0.8),
              fontSize: 14,
            ),
          ),
        )),
      ],
    );
  }
}

class _CharacterCard extends StatelessWidget {
  final String name;
  final String description;
  final String imagePath;

  const _CharacterCard({
    required this.name,
    required this.description,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 15,
            offset: const Offset(0, 15),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: const Color(0xFFF0C3E9),
                width: 5,
              ),
              image: DecorationImage(
                image: AssetImage(imagePath),
                fit: BoxFit.cover,
              ),
            ),
          ),
          const SizedBox(height: 15),
          Text(
            name,
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF7B5EA7),
            ),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Text(
              description,
              style: GoogleFonts.poppins(
                fontSize: 12,
                color: const Color(0xFF483C67),
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 70,
            height: 70,
            decoration: BoxDecoration(
              color: const Color(0xFFF0C3E9),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(
              icon,
              color: const Color(0xFF7B5EA7),
              size: 30,
            ),
          ),
          const SizedBox(height: 15),
          Text(
            title,
            style: GoogleFonts.poppins(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: const Color(0xFF7B5EA7),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            description,
            style: GoogleFonts.poppins(
              fontSize: 12,
              color: const Color(0xFF483C67),
              height: 1.4,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class BackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..style = PaintingStyle.fill;

    // Draw clouds
    _drawCloud(canvas, size, 0.1, 0.1, 120, 60);
    _drawCloud(canvas, size, 0.3, 0.15, 100, 50);
    _drawCloud(canvas, size, 0.25, 0.2, 80, 40);

    // Draw stars
    for (int i = 0; i < 100; i++) {
      final x = size.width * Random().nextDouble();
      final y = size.height * Random().nextDouble();
      final starPaint = Paint()
        ..color = const Color(0xFFFFE66D).withOpacity(0.2)
        ..style = PaintingStyle.fill;
      canvas.drawCircle(Offset(x, y), 2, starPaint);
    }
  }

  void _drawCloud(Canvas canvas, Size size, double x, double y, double width, double height) {
    final cloudPaint = Paint()
      ..color = Colors.white.withOpacity(0.8)
      ..style = PaintingStyle.fill;

    final path = Path();
    path.addOval(Rect.fromLTWH(
      size.width * x,
      size.height * y,
      width,
      height,
    ));
    path.addOval(Rect.fromLTWH(
      size.width * x + width * 0.2,
      size.height * y - height * 0.5,
      width * 0.7,
      width * 0.7,
    ));
    path.addOval(Rect.fromLTWH(
      size.width * x + width * 0.6,
      size.height * y - height * 0.4,
      width * 0.6,
      width * 0.6,
    ));

    canvas.drawPath(path, cloudPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
