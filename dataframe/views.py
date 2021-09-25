from rest_framework import permissions
from rest_framework import generics

from . models import Dataframe, Frame_edit_request
from . serializers import DataframeSerializer, Frame_edit_requestSerializer


# class DataframeAPI(APIView):
#     # authentication_classes = [SessionAuthentication, BasicAuthentication]
#     # permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             return Dataframe.objects.get(pk=pk)
#         except Snippet.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         chartconfig = self.get_object(pk)
#         serializer = DataframeSerializer(chartconfig)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = DataframeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(status=status.HTTP_201_CREATED)

#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class DataframeList(generics.ListCreateAPIView):
    # def get_queryset(self):
    #     return Dataframe.objects.filter(id=2)
    queryset = Dataframe.objects.all()
    serializer_class = DataframeSerializer

class DataframeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dataframe.objects.all()
    serializer_class = DataframeSerializer


class Frame_edit_requestList(generics.ListCreateAPIView):
    queryset = Frame_edit_request.objects.all()
    serializer_class = Frame_edit_requestSerializer


class Frame_edit_requestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Frame_edit_request.objects.all()
    serializer_class = Frame_edit_requestSerializer