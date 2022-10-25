﻿// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier:  Apache-2.0

namespace DynamoDB_Basics_Scenario.Tests
{
    using Xunit;
    using DynamoDB_Basics_Scenario;
    using System.Threading.Tasks;
    using Amazon.DynamoDBv2;

    [TestCaseOrderer("OrchestrationService.Project.Orderers.PriorityOrderer", "OrchestrationService.Project")]
    public class DynamoDbMethodsTests
    {
        readonly AmazonDynamoDBClient client = new();
        readonly string tableName = "movie_table";
        readonly string movieFileName = "moviedata.json";
        readonly string testMovieFileName = "testmoviedata.json";

        [Fact, TestPriority(1)]
        public async Task CreateMovieTableAsyncTest()
        {
            var success = await DynamoDbMethods.CreateMovieTableAsync(client, tableName);

            Assert.True(success, "Failed to create table.");
        }

        [Fact, TestPriority(2)]
        public async Task PutItemAsyncTest()
        {
            var newMovie = new Movie
            {
                Year = 1959,
                Title = "North by Northwest",
            };

            var success = await DynamoDbMethods.PutItemAsync(client, newMovie, tableName);
            Assert.True(success, "Couldn't add the movie.");
        }

        [Fact, TestPriority(3)]
        public async Task UpdateItemAsyncTest()
        {
            var updateMovie = new Movie
            {
                Title = "Now You See Me",
                Year = 2013,
            };

            var updateMovieInfo = new MovieInfo
            {
                Plot = "An FBI agent and an Interpol detective track a team of illusionists who pull off bank heists during their performances and share the wealth with the audience.",
                Rank = 5,
            };

            var success = await DynamoDbMethods.UpdateItemAsync(client, updateMovie, updateMovieInfo, tableName);
            Assert.True(success, $"Couldn't update {updateMovie.Title}.");
        }

        [Fact, TestPriority(4)]
        public async Task GetItemAsyncTest()
        {
            var lookupMovie = new Movie
            {
                Title = "Now You See Me",
                Year = 2013,
            };

            var item = await DynamoDbMethods.GetItemAsync(client, lookupMovie, tableName);

            Assert.True(item["title"].S == lookupMovie.Title, $"Couldn't find {lookupMovie.Title}.");
        }

        [Fact, TestPriority(5)]
        public void ImportMoviesWithBadFileNameShouldReturnNullTest()
        {
            var movies = DynamoDbMethods.ImportMovies(testMovieFileName);
            Assert.Null(movies);
        }

        [Fact, TestPriority(6)]
        public void ImportMoviesWithGoodFileNameShouldReturnList()
        {
            var movies = DynamoDbMethods.ImportMovies(movieFileName);
            Assert.NotNull(movies);
        }

        [Fact, TestPriority(7)]
        public async Task BatchWriteItemsAsyncTest()
        {
            var itemCount = await DynamoDbMethods.BatchWriteItemsAsync(client, movieFileName);
            Assert.Equal(250, itemCount);
        }

        [Fact, TestPriority(8)]
        public async Task DeleteItemAsyncTest()
        {
            var movieToDelete = new Movie
            {
                Title = "Gravity",
                Year = 2013,
            };

            var success = await DynamoDbMethods.DeleteItemAsync(client, tableName, movieToDelete);
            Assert.True(success, "Couldn't delete the item.");
        }

        [Fact, TestPriority(9)]
        public async Task QueryMoviesAsyncTest()
        {
            // Use Query to find all the movies released in 2010.
            int findYear = 2013;
            var queryCount = await DynamoDbMethods.QueryMoviesAsync(client, tableName, findYear);
            Assert.True(queryCount > 0, "Couldn't find any movies that match.");
        }

        [Fact, TestPriority(10)]
        public async Task ScanTableAsyncTest()
        {
            int startYear = 2001;
            int endYear = 2011;
            var scanCount = await DynamoDbMethods.ScanTableAsync(client, tableName, startYear, endYear);
            Assert.True(scanCount > 0, "Couldn't find any movies released in those years.");
        }

        [Fact, TestPriority(11)]
        public async void DeleteTableAsyncTest()
        {
            var success = await DynamoDbMethods.DeleteTableAsync(client, tableName);

            Assert.True(success, "Failed to delete table.");
        }
    }
}