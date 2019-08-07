from collections import defaultdict

from django.conf import settings
from django.db import models, transaction
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField
from rest_framework import serializers

from pol_harvester.models import Freeze


class QueryRanking(models.Model):

    query = models.ForeignKey("search.Query")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    subquery = models.CharField(max_length=255, db_index=True)
    ranking = JSONField(default={})
    freeze = models.ForeignKey(Freeze, on_delete=models.SET_NULL, null=True)
    is_approved = models.NullBooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_elastic_ratings(self, as_dict=False):
        ratings = [
            {
                "_index": key.split(":")[0],
                "_id": key.split(":")[1],
                "rating": value
            }
            for key, value in self.ranking.items()
        ]
        return ratings if not as_dict else {rating["_id"]:rating["rating"] for rating in ratings}


class ListFromUserSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        request = self.context["request"]
        data = data.filter(user=request.user)
        return super().to_representation(data)


class UserQueryRankingSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryRanking
        list_serializer_class = ListFromUserSerializer
        fields = ("subquery", "ranking", "freeze")


class QueryManager(models.Manager):

    def get_query_rankings(self, freeze, user):
        rankings = defaultdict(dict)
        for ranking in QueryRanking.objects.filter(freeze=freeze, user=user):
            rankings[ranking.query].update(ranking.get_elastic_ratings(as_dict=True))
        return rankings


class Query(models.Model):

    objects = QueryManager()

    query = models.CharField(max_length=255, db_index=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=QueryRanking)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_elastic_query_body(self, fields, enrichment=None):
        enrichment = enrichment or []
        query = "{} {}".format(self.query, " ".join(enrichment)).strip()
        return {
            'bool': {
                'must': [
                    {
                        "multi_match": {
                            "fields": fields,
                            "fuzziness": 0,
                            "operator": "or",
                            "query": query,
                            "type": "best_fields",
                            "tie_breaker": 0.3
                        }
                    }
                ],
                'should': [
                    {
                        "multi_match": {
                            "fields": fields,
                            "query": query,
                            "type": "phrase"
                        }
                    }
                ]
            }
        }

    def get_elastic_ranking_request(self, freeze, user, fields):
        ratings = []
        for ranking in self.queryranking_set.filter(freeze=freeze, user=user):
            ratings += ranking.get_elastic_ratings()
        return {
            "id": slugify(self.query),
            "request": {
                "query": self.get_elastic_query_body(fields)
            },
            "ratings": ratings
        }

    class Meta:
        verbose_name_plural = "queries"


class QuerySerializer(serializers.ModelSerializer):

    rankings = UserQueryRankingSerializer(source="queryranking_set", many=True, read_only=False, allow_null=False,
                                          required=True)

    def validate(self, data):
        data = super().validate(data)
        query = data["query"]
        for ranking in data["queryranking_set"]:
            if query == ranking["subquery"]:
                break
        else:
            raise serializers.ValidationError("At least one ranking must be specified with the main query as subquery")
        return data

    def build_query_rankings(self, instance, user, validated_data):
        rankings = []
        instance.queryranking_set.filter(user=user).delete()
        for ranking in validated_data:
            rankings.append(QueryRanking(user=user, query=instance, **ranking))
        QueryRanking.objects.bulk_create(rankings)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        query, created = Query.objects.get_or_create(query=validated_data["query"])
        self.build_query_rankings(query, request.user, validated_data["queryranking_set"])
        return query

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context["request"]
        self.build_query_rankings(instance, request.user, validated_data["queryranking_set"])
        return instance

    class Meta:
        model = Query
        fields = ("query", "rankings", "created_at", "modified_at",)
