from rest_framework import serializers
from .models import Article, Content, Course, Hyperlink, Quiz, VideoPlayer,UserPerformance
from youtube_transcript_api import YouTubeTranscriptApi
from .models import VideoTranscript
import re
from .models import Article

class CourseSerializer(serializers.ModelSerializer):
    user_performance = serializers.SerializerMethodField()  # Custom field for performance
    articles = serializers.SerializerMethodField()  # Custom field for concatenated article names

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'slug', 'total_videos', 'user_performance', 'articles']

    def get_user_performance(self, obj):
        user = self.context.get('user')  # Expecting user in context
        if user:
            # Fetch user performance for the course
            performance = UserPerformance.objects.filter(user=user, course=obj).first()
            if performance:
                # If performance exists, calculate based on watched videos
                watched_videos_count = performance.watched_videos.count()
                total_videos_count = obj.total_videos  # Assuming you have a total_videos field
                progress = (watched_videos_count / total_videos_count) * 100 if total_videos_count > 0 else 0
                return {
                    "user": user.id,
                    "watched_videos": list(performance.watched_videos.values_list('id', flat=True)),
                    "progress": progress
                }
            else:
                # Return default progress of 50% if no performance data exists
                return {
                    "user": user.id,
                    "watched_videos": [],
                    "progress": 50  # Default progress is 50%
                }
        return None  # Return None if no user is in context

    def get_articles(self, obj):
        # Retrieve all articles related to the course
        articles = Article.objects.filter(course_name=obj)
        # Concatenate article names separated by semicolons
        article_names = ";".join(article.article_name for article in articles)
        return article_names


class HyperlinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hyperlink
        fields = ['hyper_link_word', 'hyper_link_word_url']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'article', 'question', 'options', 'opt_values', 'correct_options']

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['content_id','content_name']

import re



class VideoPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPlayer
        fields = ['video_played_id', 'video_title', 'video_description', 'channel_name']


class ArticleSerializer(serializers.ModelSerializer):
    hyperlinks = HyperlinkSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)
    content = ContentSerializer(many=True, read_only=True)
    videos = VideoPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'course_name',
            'article_name',
            'slug',
            'description',
            'article_video_thumbnail',
            'article_video_url',
            'subtitles',  # Include subtitles in the fields
            'hyperlinks',
            'quizzes',
            'content',
            'videos',
        ]

    def create(self, validated_data):
        article = super().create(validated_data)
        self.fetch_and_save_subtitles(article)
        return article

    def update(self, instance, validated_data):
        article = super().update(instance, validated_data)
        self.fetch_and_save_subtitles(article)
        return article

    def fetch_and_save_subtitles(self, article):
        video_url = article.article_video_url
        video_id = self.extract_video_id(video_url)

        if not video_id:
            print("Error: No video ID found in URL.")
            return

        try:
            # Fetch subtitles using YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([item['text'] for item in transcript])  # Join transcript into a string
            article.subtitles = transcript_text
            article.save()  # Save subtitles to the database
        except Exception as e:
            print(f"Error fetching subtitles: {e}")

    def extract_video_id(self, url):
        # Regular expression to extract YouTube video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        video_id = video_id_match.group(1) if video_id_match else None
        print(f"Extracted video ID: {video_id}")  # Debug print
        return video_id



class VideoTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTranscript
        fields = ['youtube_url', 'transcript']


# class UserPerformanceSerializer(serializers.ModelSerializer):
#     watched_video_ids = serializers.ListField(
#         child=serializers.CharField(), write_only=True, required=False
#     )
#     watched_video_ids_readonly = serializers.SerializerMethodField()  # Read-only calculated field
#     progress = serializers.SerializerMethodField()  # Read-only calculated field

#     class Meta:
#         model = UserPerformance
#         fields = ['user', 'course', 'watched_video_ids', 'watched_video_ids_readonly', 'progress']

#     def create(self, validated_data):
#         watched_video_ids = validated_data.pop('watched_video_ids', [])
#         performance = UserPerformance(**validated_data)
#         performance.save()
#         performance.set_watched_video_ids(watched_video_ids)
#         return performance

#     def update(self, instance, validated_data):
#         watched_video_ids = validated_data.pop('watched_video_ids', None)

#         if watched_video_ids is not None:
#             instance.set_watched_video_ids(watched_video_ids)
#         instance.save()
#         return instance

#     def get_watched_video_ids_readonly(self, obj):
#         return obj.get_watched_video_ids()
#     def get_progress(self, obj):
    
#         total_videos = obj.course.total_videos  
#         watched_videos = len(obj.get_watched_video_ids())
#         return (watched_videos / total_videos) * 100 if total_videos > 0 else 0
# Import your UserPerformance model

class UserPerformanceSerializer(serializers.ModelSerializer):
    watched_video_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    watched_video_ids_readonly = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = UserPerformance
        fields = ['user', 'user_id', 'course', 'watched_video_ids', 'watched_video_ids_readonly', 'progress']

    def create(self, validated_data):
        watched_video_ids = set(validated_data.pop('watched_video_ids', []))  # Ensure unique IDs
        performance = UserPerformance(**validated_data)
        performance.save()
        performance.set_watched_video_ids(list(watched_video_ids))
        return performance

    def update(self, instance, validated_data):
        watched_video_ids = validated_data.pop('watched_video_ids', None)
        if watched_video_ids is not None:
            instance.set_watched_video_ids(list(set(watched_video_ids)))  # Ensure unique IDs
        instance.save()
        return instance

    def get_watched_video_ids_readonly(self, obj):
        return obj.get_watched_video_ids()

    def get_progress(self, obj):
        watched_videos_count = obj.watched_videos.count()  # Count the watched videos
        total_videos = obj.course.total_videos if obj.course else 0  # Access total_videos correctly

        # If total_videos is None, default to 0
        if total_videos is None:
            total_videos = 0  

        return (watched_videos_count / total_videos) * 100 if total_videos > 0 else 0


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_id'] = instance.user.id  # Add user ID to the representation
        return representation


# class UserPerformanceSerializer(serializers.ModelSerializer):
#     watched_video_ids = serializers.ListField(
#         child=serializers.CharField(), write_only=True, required=False
#     )
#     watched_video_ids_readonly = serializers.SerializerMethodField()
#     progress = serializers.SerializerMethodField()

#     class Meta:
#         model = UserPerformance
#         fields = ['user', 'course', 'watched_video_ids', 'watched_video_ids_readonly', 'progress']

#     def create(self, validated_data):
#         watched_video_ids = set(validated_data.pop('watched_video_ids', []))  # Ensure unique IDs
#         performance = UserPerformance(**validated_data)
#         performance.save()
#         performance.set_watched_video_ids(list(watched_video_ids))
#         return performance

#     def update(self, instance, validated_data):
#         watched_video_ids = validated_data.pop('watched_video_ids', None)
#         if watched_video_ids is not None:
#             instance.set_watched_video_ids(list(set(watched_video_ids)))  # Ensure unique IDs
#         instance.save()
#         return instance

#     def get_watched_video_ids_readonly(self, obj):
#         return obj.get_watched_video_ids()

#     def get_progress(self, obj):
#         total_videos = obj.course.total_videos  
#         watched_videos = len(obj.get_watched_video_ids())
#         return (watched_videos / total_videos) * 100 if total_videos > 0 else 0


class VideoPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPlayer
        fields = [
            'video_played_id',
            'video_title',
            'video_description',
            'channel_name'
        ]



        
